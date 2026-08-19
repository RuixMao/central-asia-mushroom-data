"""价格合理区间校验。

区间按 (species_id, country) 配置；当前通用物种区间使用 "*" 国家，
后续可在表中增加国家覆盖项，例如 ("button_mushroom", "KG")。
超出区间只标记待复核，不删除原始价格。
"""

SANITY_BANDS = {
    ("button_mushroom", "*"): (2.0, 20.0),
    ("oyster_mushroom", "*"): (1.0, 15.0),
    ("shiitake", "*"): (5.0, 40.0),
    ("*", "*"): (1.0, 50.0),
}


def sanity_band(species_id, country):
    return SANITY_BANDS.get((species_id, country), SANITY_BANDS.get((species_id, "*"), SANITY_BANDS[("*", "*")]))


def check_usd_per_kg(species_id, country, usd_per_kg):
    low, high = sanity_band(species_id, country)
    outlier = usd_per_kg is not None and not (low <= float(usd_per_kg) <= high)
    return {
        "sanity_outlier": outlier,
        "sanity_reason": f"超出合理区间({low:g}~{high:g} USD/kg)" if outlier else None,
        "sanity_min_usd_per_kg": low,
        "sanity_max_usd_per_kg": high,
    }


def apply_sanity_validation(review, species_id, country, usd_per_kg):
    """把区间结果合并进既有复核结论；原有 rejected 状态不覆盖。"""
    sanity = check_usd_per_kg(species_id, country, usd_per_kg)
    reasons = list(review.get("reasons") or [])
    actions = list(review.get("actions") or [])
    status = review["validation_status"]
    decision = review["decision"]
    if sanity["sanity_outlier"] and status != "rejected":
        status = "needs_review"
        decision = "manual_review"
        reasons.append("sanity_outlier")
        actions.append("核对商品等级、运费、促销、净重与页面解析")
    return {
        **sanity,
        "validation_status": status,
        "review_decision": decision,
        "review_reasons": list(dict.fromkeys(reasons)),
        "review_actions": list(dict.fromkeys(actions)),
    }


def _median(values):
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2


def review_sanity_outliers(items):
    """用同国、同品类、同形态的有效商品规格自动解释异常价。

    只有页面已明确解析出净重，且异常商品为不超过 500g 的小包装、
    对照商品包装至少大 2 倍、公斤价至少相差 2 倍时，才把小包装列为
    最大可能原因。异常记录仍保持 needs_review，不重新放回聚合。
    """
    valid = [item for item in items if item.get("validation_status") == "valid"]
    reviewed = 0
    for item in items:
        if not item.get("sanity_outlier"):
            item.setdefault("sanity_review_status", "not_required")
            item.setdefault("sanity_review_reason", None)
            continue
        item["sanity_review_status"] = "pending"
        item["sanity_review_reason"] = "具体原因待查"
        quantity = item.get("normalized_quantity_kg")
        price = item.get("normalized_price_usd_per_kg")
        if not quantity or not price or float(quantity) > 0.5:
            continue
        peers = [peer for peer in valid if peer.get("country") == item.get("country")
                 and peer.get("species_id") == item.get("species_id")
                 and peer.get("product_form") == item.get("product_form")
                 and peer.get("normalized_quantity_kg") and peer.get("normalized_price_usd_per_kg")]
        if not peers:
            continue
        peer_quantity = _median([peer["normalized_quantity_kg"] for peer in peers])
        peer_price = _median([peer["normalized_price_usd_per_kg"] for peer in peers])
        if peer_quantity < float(quantity) * 2 or float(price) < peer_price * 2:
            continue
        grams = round(float(quantity) * 1000)
        peer_grams = round(peer_quantity * 1000)
        reason = (f"自动复核：商品标题明确标注{grams}g小包装；同国同品类有效对照以"
                  f"{peer_grams}g包装为主，其公斤价约{peer_price:.2f} USD/kg。"
                  "小包装规格溢价是该价格差异的最大可能因素")
        item["sanity_review_status"] = "explained"
        item["sanity_review_reason"] = reason
        item["sanity_reason"] = f'{item.get("sanity_reason") or "价格异常"}；{reason}'
        reviewed += 1
    return reviewed
