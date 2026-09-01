import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from generate_report import customer_safe, customer_visible_price, display_usd_per_kg, select_report_prices, title_from, utf8_truncate


def test_display_usd_per_kg_formats_numeric_price():
    assert display_usd_per_kg("42.84") == "42.84"


def test_display_usd_per_kg_handles_missing_or_invalid_price():
    assert display_usd_per_kg(None) == "—"
    assert display_usd_per_kg("") == "—"


def test_customer_visible_price_rejects_pending_missing_and_generic_rows():
    base={"status":"live","validation_status":"valid","sanity_outlier":False,"species_id":"button_mushroom","package_display":"300 g","normalized_price_usd_per_kg":5.92,"price_local":520,"currency":"KGS","package_source":"page_title"}
    assert customer_visible_price({"data":base})
    assert not customer_visible_price({"data":{**base,"validation_status":"needs_review"}})
    assert not customer_visible_price({"data":{**base,"package_display":None}})
    assert not customer_visible_price({"data":{**base,"species_id":"unknown"}})


def test_customer_safe_rejects_pending_sections_and_empty_references():
    sections="\n".join(f"## {name}\n"+"已确认价格依据充分。"*20 for name in ("今日要点","市场动态","机会与风险","行动建议","数据说明"))
    assert customer_safe(sections,set())
    assert not customer_safe(sections.replace("已确认价格", "原因待进一步确认",1),set())
    assert not customer_safe(sections.replace("已确认价格", "详见正文事实条目",1),set())


def test_title_uses_verified_same_species_spread():
    prices=[
        {"country":"KG","data":{"species_id":"button_mushroom","normalized_price_usd_per_kg":4.90}},
        {"country":"TM","data":{"species_id":"button_mushroom","normalized_price_usd_per_kg":17.50}},
    ]
    title=title_from("2026-08-20","## 今日要点\n\n**内部标题不应采用。**",prices)
    assert title.endswith("双孢菇价差3.6倍")
    assert len(title.encode("utf-8")) <= 64
    assert "待确认" not in title


def test_report_prices_backfill_missing_southeast_asia_with_recent_rows():
    def row(country, observed_at, product):
        return {"country": country, "data": {"observed_at": observed_at, "product_key": product, "species_id": "oyster_mushroom", "normalized_price_usd_per_kg": 1}}

    live = [
        row("KZ", "2026-09-01", "kz-today"),
        row("LA", "2026-08-31", "la-latest"),
        {"country": "LA", "data": {"observed_at": "2026-08-31", "product_key": "la-second", "species_id": "shiitake", "normalized_price_usd_per_kg": 2}},
        {"country": "LA", "data": {"observed_at": "2026-08-31", "product_key": "la-third", "species_id": "enoki", "normalized_price_usd_per_kg": 3}},
        row("LA", "2026-08-29", "la-older"),
        row("VN", "2026-08-31", "vn-latest"),
        row("TH", "2026-08-20", "th-too-old"),
    ]
    selected = select_report_prices(live, "2026-09-01")
    keys = {item["data"]["product_key"] for item in selected}
    assert "kz-today" in keys and "vn-latest" in keys
    assert len([item for item in selected if item["country"] == "LA"]) == 2


def test_title_does_not_mix_historical_prices_into_today_spread():
    prices = [
        {"country": "KG", "data": {"species_id": "button_mushroom", "normalized_price_usd_per_kg": 4.90, "observed_at": "2026-09-01"}},
        {"country": "TH", "data": {"species_id": "button_mushroom", "normalized_price_usd_per_kg": 17.50, "observed_at": "2026-08-31"}},
    ]
    title = title_from("2026-09-01", "## 今日要点\n\n**市场平稳无异常。**", prices)
    assert "价差" not in title


def test_utf8_truncate_never_splits_chinese_character():
    value=utf8_truncate("五国双孢菇价差明显",10)
    assert len(value.encode("utf-8"))<=10
    value.encode("utf-8").decode("utf-8")
