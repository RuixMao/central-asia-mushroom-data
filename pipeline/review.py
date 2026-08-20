"""价格记录的确定性自动复核。

只有品类、价格和规格都有页面证据时才自动通过。
罐装菌类采用市场口径 1 L = 1 kg，同时保留原始体积和换算依据。
宽泛菌名和缺少规格不由模型猜测，保留给人工或二次证据采集。
"""


MASS_EVIDENCE_SOURCES = {"page_title", "page_structured_data"}
VOLUME_EVIDENCE_SOURCES = {"page_title_volume_estimate", "page_structured_volume_estimate"}


def review_record(record):
    reasons = []
    actions = []

    if record.get("classification_status") == "excluded":
        return {"decision": "auto_reject", "validation_status": "rejected", "reasons": ["non_food_or_excluded"], "actions": []}

    if record.get("classification_status") != "classified" or not record.get("species_id"):
        reasons.append("species_ambiguous")
        actions.append("confirm_species_from_product_page_or_image")
    elif float(record.get("classification_confidence") or 0) < 0.9:
        reasons.append("species_confidence_low")
        actions.append("confirm_species_from_product_page_or_image")

    package_source = record.get("package_source") or "unverified"
    if package_source in VOLUME_EVIDENCE_SOURCES:
        if not record.get("normalized_quantity_kg") or not record.get("package_conversion_basis"):
            reasons.append("volume_conversion_missing")
            actions.append("apply_one_litre_equals_one_kilogram_policy")
    elif package_source not in MASS_EVIDENCE_SOURCES or not record.get("normalized_quantity_kg"):
        reasons.append("net_weight_missing")
        actions.append("find_net_weight_on_page_or_package_image")

    if record.get("current_price") is None or float(record.get("current_price") or 0) <= 0:
        reasons.append("price_missing_or_invalid")
        actions.append("confirm_current_price_and_currency")

    if reasons:
        return {"decision": "manual_review", "validation_status": "needs_review", "reasons": reasons, "actions": list(dict.fromkeys(actions))}
    return {"decision": "auto_approve", "validation_status": "valid", "reasons": [], "actions": []}
