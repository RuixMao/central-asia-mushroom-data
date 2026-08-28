"""One-time backfill for a retailer listing where the package size is not exposed."""

import datetime as dt

from utils import post_to_site, safe_get, log


SOURCE_DATE = "2026-08-28"
SOURCE_URL = "https://www.foodpanda.la/en/shop/s8f0/champa-market"


def build_items(local_per_usd):
    observed_at = dt.datetime.fromisoformat(f"{SOURCE_DATE}T12:00:00+07:00").isoformat()
    return [{
        "platform": "foodpanda-champa-market-la",
        "platform_name": "Foodpanda Laos / Champa Market",
        "platform_product_id": "indexed-enoki-listing-20260828",
        "country": "LA",
        "city": "Vientiane",
        "collection_point_id": "VIENTIANE_POINT_01",
        "product_url": SOURCE_URL,
        "original_title": "ເຫັດເຂັມ",
        "original_description": "Foodpanda Champa Market online retail listing",
        "original_category": "ຜັກ/ໝາກໄມ້",
        "original_language": "lo",
        "species_id": "enoki",
        "product_form": "fresh",
        "classification_status": "classified",
        "classification_confidence": 1.0,
        "classification_evidence": {"title": "ເຫັດເຂັມ", "rule": "lao_enoki_dictionary"},
        "observed_at": observed_at,
        "observation_date": SOURCE_DATE,
        "current_price": 15000,
        "currency": "LAK",
        "package_value": None,
        "package_unit": None,
        "normalized_quantity_kg": None,
        "normalized_price_per_kg": None,
        "price_usd": round(15000 / local_per_usd, 2),
        "usd_rate_local_per_usd": local_per_usd,
        "fx_source": "fxapi.app",
        "fx_timestamp": None,
        "in_stock": None,
        "raw_price_text": "₭ 15,000",
        "source_type": "retailer_search_listing",
        "validation_status": "valid",
        "review_reasons": ["relaxed_missing_package: retailer listing omits net weight"],
        "sanity_outlier": False,
        "sanity_reason": None,
    }]


def run():
    response = safe_get("https://fxapi.app/api/usd.json", retries=2)
    items = build_items(float(response.json()["rates"]["LAK"]))
    result = post_to_site("/api/ingest/prices", {"items": items})
    log(f"Laos relaxed retail listings written: {len(items)}; result={result}")


if __name__ == "__main__":
    run()
