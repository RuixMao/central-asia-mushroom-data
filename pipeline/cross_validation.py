"""为价格记录建立独立于单页解析的第二层证据。

原始记录始终保留；只有源页面证据之外，再得到跨日复采、详情接口复核，
或独立渠道价格带支持的记录，才保持 ``validation_status=valid``。
"""

from collections import Counter


def _number(value):
    try:
        number = float(value)
        return number if number > 0 else None
    except (TypeError, ValueError):
        return None


def _ratio(a, b):
    return max(a, b) / min(a, b) if a and b else float("inf")


def _history_rows(records):
    rows = []
    for record in records or []:
        data = record.get("data") or {}
        value = _number(data.get("normalized_price_usd_per_kg"))
        if data.get("status") != "live" or value is None:
            continue
        rows.append({
            "country": record.get("country"),
            "platform": data.get("platform_id") or record.get("source"),
            "product_key": data.get("product_key"),
            "species_id": data.get("species_id"),
            "product_form": data.get("product_form"),
            "value": value,
            "observed_at": data.get("observed_at"),
            "grade": data.get("grade"),
            "source_type": data.get("source_type"),
            "cross_validation_status": data.get("cross_validation_status"),
            "candidate_attempt": int(data.get("candidate_attempt") or 0),
        })
    return rows


def cross_validate_prices(items, historical_records=None, *, repeat_tolerance=0.10, peer_ratio=2.5):
    """以加权且来源独立的证据判定价格是否可进入客户版。"""
    history = _history_rows(historical_records)
    stats = Counter(scanned=len(items))
    current = []
    for item in items:
        value = _number(item.get("normalized_price_usd_per_kg"))
        if value is None:
            continue
        current.append({
            "item": item,
            "country": item.get("country"),
            "platform": item.get("platform"),
            "species_id": item.get("species_id"),
            "product_form": item.get("product_form"),
            "value": value,
        })

    for row in current:
        item = row["item"]
        if item.get("validation_status") != "valid":
            stats["not_eligible"] += 1
            continue
        evidence = [{"type": "source_page", "source": item.get("product_url"), "weight": 40}]
        risk_flags = []
        if item.get("detail_verified"):
            evidence.append({"type": "detail_recheck", "source": item.get("platform"), "weight": 25})

        product_key = f'{item.get("platform")}:{item.get("collection_point_id")}:{item.get("platform_product_id")}'
        prior_candidates = [old for old in history if old["product_key"] == product_key
                            and old.get("cross_validation_status") == "pending"]
        attempt = max([old.get("candidate_attempt", 0) for old in prior_candidates] or [0]) + 1
        item["candidate_attempt"] = attempt
        repeats = [old for old in history if old["product_key"] == product_key
                   and _ratio(row["value"], old["value"]) <= 1 + repeat_tolerance]
        if repeats:
            latest = repeats[0]
            evidence.append({"type": "repeat_observation", "observed_at": latest.get("observed_at"),
                             "price_usd_per_kg": latest["value"], "weight": 30})

        peers = [peer for peer in current if peer is not row
                 and peer["country"] == row["country"]
                 and peer["species_id"] == row["species_id"]
                 and peer["product_form"] == row["product_form"]
                 and peer["platform"] != row["platform"]
                 and _ratio(row["value"], peer["value"]) <= peer_ratio]
        historical_peers = [old for old in history
                     if old["country"] == row["country"]
                     and old["species_id"] == row["species_id"]
                     and old["product_form"] == row["product_form"]
                     and old["platform"] != row["platform"]]
        peers.extend(old for old in historical_peers if _ratio(row["value"], old["value"]) <= peer_ratio)
        if peers:
            peer = peers[0]
            third_party = peer.get("grade") in {"C", "D"} or peer.get("source_type") in {
                "official_statistics", "industry_report", "trade_database", "third_party_audit"
            }
            evidence.append({"type": "third_party_anchor" if third_party else "independent_channel",
                             "source": peer.get("platform"), "price_usd_per_kg": peer["value"],
                             "weight": 25})
        if any(_ratio(row["value"], peer["value"]) > 4 for peer in historical_peers):
            risk_flags.append("independent_source_price_conflict")

        item["verification_evidence"] = evidence
        score = min(100, sum(entry["weight"] for entry in evidence))
        if risk_flags:
            score = max(0, score - 15)
        item["verification_method_version"] = "smart-v1"
        item["verification_score"] = score
        item["verification_risk_flags"] = risk_flags
        if score >= 65:
            item["cross_validation_status"] = "verified"
            item["candidate_state"] = "promoted"
            item["candidate_next_action"] = None
            stats["verified"] += 1
        else:
            item["cross_validation_status"] = "pending"
            item["validation_status"] = "needs_review"
            if risk_flags:
                state, action = "conflict_review", "recheck_source_and_compare_independent_channel"
            elif attempt == 1:
                state, action = "awaiting_recheck", "recollect_same_product_next_run"
            elif attempt == 2:
                state, action = "seeking_independent_source", "collect_independent_channel_or_third_party_anchor"
            else:
                state, action = "archived_unconfirmed", "retain_raw_record_and_reopen_only_with_new_evidence"
            item["candidate_state"] = state
            item["candidate_next_action"] = action
            item["review_decision"] = "auto_archive" if state == "archived_unconfirmed" else "cross_check_required"
            item["review_reasons"] = list(dict.fromkeys([*(item.get("review_reasons") or []), "cross_validation_insufficient"]))
            item["review_actions"] = list(dict.fromkeys([*(item.get("review_actions") or []), action]))
            stats["pending"] += 1
            stats[state] += 1
    return dict(stats)
