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
        })
    return rows


def cross_validate_prices(items, historical_records=None, *, repeat_tolerance=0.10, peer_ratio=2.5):
    """就地写入交叉验证证据，并返回本轮统计。"""
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
        evidence = [{"type": "source_page", "source": item.get("product_url")}]
        if item.get("detail_verified"):
            evidence.append({"type": "detail_recheck", "source": item.get("platform")})

        product_key = f'{item.get("platform")}:{item.get("collection_point_id")}:{item.get("platform_product_id")}'
        repeats = [old for old in history if old["product_key"] == product_key
                   and _ratio(row["value"], old["value"]) <= 1 + repeat_tolerance]
        if repeats:
            latest = repeats[0]
            evidence.append({"type": "repeat_observation", "observed_at": latest.get("observed_at"),
                             "price_usd_per_kg": latest["value"]})

        peers = [peer for peer in current if peer is not row
                 and peer["country"] == row["country"]
                 and peer["species_id"] == row["species_id"]
                 and peer["product_form"] == row["product_form"]
                 and peer["platform"] != row["platform"]
                 and _ratio(row["value"], peer["value"]) <= peer_ratio]
        peers.extend(old for old in history
                     if old["country"] == row["country"]
                     and old["species_id"] == row["species_id"]
                     and old["product_form"] == row["product_form"]
                     and old["platform"] != row["platform"]
                     and _ratio(row["value"], old["value"]) <= peer_ratio)
        if peers:
            peer = peers[0]
            evidence.append({"type": "independent_channel", "source": peer.get("platform"),
                             "price_usd_per_kg": peer["value"]})

        item["verification_evidence"] = evidence
        item["verification_score"] = len(evidence)
        if len(evidence) >= 2:
            item["cross_validation_status"] = "verified"
            stats["verified"] += 1
        else:
            item["cross_validation_status"] = "pending"
            item["validation_status"] = "needs_review"
            item["review_decision"] = "cross_check_required"
            item["review_reasons"] = list(dict.fromkeys([*(item.get("review_reasons") or []), "cross_validation_insufficient"]))
            item["review_actions"] = list(dict.fromkeys([*(item.get("review_actions") or []), "repeat_or_confirm_with_independent_channel"]))
            stats["pending"] += 1
    return dict(stats)
