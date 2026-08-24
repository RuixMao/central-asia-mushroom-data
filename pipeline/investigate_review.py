"""对首轮未通过的价格记录执行有针对性的二次证据检索。"""

import json

from bs4 import BeautifulSoup

from review import review_record
from sanity import apply_sanity_validation
from taxonomy import classify, normalize_price
from utils import safe_get


def _page_evidence(response):
    html = getattr(response, "text", "") or ""
    soup = BeautifulSoup(html, "html.parser")
    values = []
    if soup.title:
        values.append(soup.title.get_text(" ", strip=True))
    for key in ("description", "og:title", "og:description"):
        node = soup.find("meta", attrs={"name": key}) or soup.find("meta", attrs={"property": key})
        if node and node.get("content"):
            values.append(node["content"])
    for node in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(node.string or "")
        except (TypeError, json.JSONDecodeError):
            continue
        # JSON-LD 是页面提供的结构化证据；只提取商品描述相关字段。
        stack = payload if isinstance(payload, list) else [payload]
        for entry in stack:
            if not isinstance(entry, dict):
                continue
            for field in ("name", "description", "size", "weight"):
                value = entry.get(field)
                if isinstance(value, dict):
                    value = " ".join(str(value.get(k, "")) for k in ("value", "unitText", "unitCode"))
                if isinstance(value, (str, int, float)):
                    values.append(str(value))
    return " ".join(dict.fromkeys(x for x in values if x))


def investigate_record(record, fetcher=safe_get):
    """按失败原因重新读取原商品页，并用新证据再次运行同一套硬规则。"""
    if record.get("validation_status") != "needs_review":
        return False
    reasons = set(record.get("review_reasons") or [])
    searchable = {"net_weight_missing", "volume_conversion_missing", "species_ambiguous", "species_confidence_low"}
    if not reasons.intersection(searchable) or not record.get("product_url"):
        return False
    response = fetcher(record["product_url"])
    if response is None:
        record["investigation_status"] = "source_unavailable"
        return False
    evidence = _page_evidence(response)
    if not evidence:
        record["investigation_status"] = "no_new_evidence"
        return False

    if reasons.intersection({"species_ambiguous", "species_confidence_low"}):
        category = classify(record.get("original_title") or "", description=evidence,
                            category=record.get("original_category") or "",
                            language=record.get("original_language") or "")
        if category["status"] == "classified":
            record.update(species_id=category["species_id"], product_form=category["product_form"],
                          classification_status=category["status"],
                          classification_confidence=category["confidence"],
                          classification_evidence=category["evidence"])

    if reasons.intersection({"net_weight_missing", "volume_conversion_missing"}):
        norm = normalize_price(record.get("current_price"), evidence, allow_volume=True)
        if norm.get("quantity_kg"):
            record.update(package_value=norm["value"], package_unit=norm["unit"],
                          package_source="page_recheck", package_conversion_basis=norm.get("conversion_basis"),
                          normalized_quantity_kg=norm["quantity_kg"],
                          normalized_price_per_kg=norm["price_per_kg"])
            rate = record.get("usd_rate_local_per_usd")
            if rate and norm.get("price_per_kg") is not None:
                record["normalized_price_usd_per_kg"] = round(norm["price_per_kg"] / float(rate), 2)

    second = review_record(record)
    result = apply_sanity_validation(second, record.get("species_id"), record.get("country"),
                                     record.get("normalized_price_usd_per_kg"))
    record.update(result)
    record["investigation_status"] = "resolved" if result["validation_status"] == "valid" else "insufficient_evidence"
    record["investigation_evidence"] = evidence[:500]
    return result["validation_status"] == "valid"


def investigate_pending_reviews(items, fetcher=safe_get):
    reviewed = resolved = 0
    for item in items:
        if item.get("validation_status") != "needs_review":
            continue
        reviewed += 1
        resolved += int(investigate_record(item, fetcher=fetcher))
    return {"investigated": reviewed, "resolved": resolved}
