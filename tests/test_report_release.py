import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from report_release import build_customer_report, customer_price_is_eligible, select_customer_prices, validate_customer_report


DAY = "2026-09-28"


def observation(country="LA", product="one", **values):
    data = {"observed_at": DAY, "product_key": product, "status": "live", "validation_status": "valid", "cross_validation_status": "verified", "species_id": "oyster_mushroom", "product_form": "fresh", "package_source": "page_title", "package_display": "200 g", "price_local": 25000, "currency": "LAK", "normalized_price_usd_per_kg": 5, "price_usd": 1, "platform_name": "Retailer", "source_url": "https://example.com/product", "original_title": "Oyster Mushroom 200g"}
    data.update(values)
    return {"country": country, "source": "Retailer", "data": data}


class ReportReleaseTest(unittest.TestCase):
    def test_rejects_unverified_old_prepared_unknown_and_implausible_data(self):
        self.assertTrue(customer_price_is_eligible(observation(), DAY))
        invalid = [
            {"cross_validation_status": None}, {"observed_at": "2026-09-27"},
            {"original_title": "Thùng 50 gói cháo nấm đông cô Vifon 70g"},
            {"package_display": "1 g", "original_title": "Enoki 1g", "species_id": "enoki", "normalized_price_usd_per_kg": 1466, "price_usd": 1.466},
            {"original_title": "Dried mushroom 200g"}, {"product_form": "unknown"},
            {"package_display": "100 g"}, {"sanity_outlier_original": True},
            {"normalized_price_usd_per_kg": float("nan")}, {"source_url": ""},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                self.assertFalse(customer_price_is_eligible(observation(**changes), DAY))

    def test_selection_is_bounded_deduplicated_and_covers_all_countries(self):
        rows = [observation(country, f"{country}-{index}") for country in ("LA", "VN", "TH", "MM", "KH", "KZ", "UZ", "KG", "TJ", "TM") for index in range(5)]
        original = copy.deepcopy(rows)
        selected = select_customer_prices(rows + rows, DAY)
        self.assertEqual(len(selected), 20)
        self.assertEqual(len({row["country"] for row in selected}), 10)
        self.assertEqual(rows, original)
        self.assertEqual(len(select_customer_prices([observation("LA", str(index)) for index in range(20)], DAY)), 2)

    def test_report_has_five_sections_short_title_and_separate_forms(self):
        rows = [observation(country, f"{country}-{index}", product_form="dried" if index == 1 else "fresh") for country in ("LA", "VN", "TH", "MM", "KH", "KZ", "UZ", "KG", "TJ", "TM") for index in range(2)]
        report = build_customer_report(DAY, rows)
        headings = [line for line in report["body"].splitlines() if line.startswith("## ")]
        self.assertEqual(headings, ["## 今日要点", "## 市场动态", "## 机会与风险", "## 行动建议", "## 数据说明"])
        self.assertLessEqual(len(report["title"].encode("utf-8")), 64)
        self.assertIn("### 干品", report["body"])
        self.assertIn("### 鲜品", report["body"])
        for word in ("1466", "精品", "复核", "待确认", "样本", "https://", "口径", "自动"):
            self.assertNotIn(word, report["body"])
        for country in ("老挝", "越南", "泰国", "缅甸", "柬埔寨", "哈萨克斯坦", "土库曼斯坦"):
            self.assertIn(country, report["body"])

    def test_empty_release_is_refused(self):
        with self.assertRaises(ValueError):
            build_customer_report(DAY, [observation(cross_validation_status="pending")])

    def test_release_remains_compatible_with_downstream_content_package(self):
        from generate_content_package import build_package
        rows = [observation(country, f"{country}-{index}") for country in ("LA", "VN", "TH", "MM", "KH", "KZ", "UZ", "KG", "TJ", "TM") for index in range(2)]
        report = build_customer_report(DAY, rows)
        package = build_package({**report, "date": DAY})
        self.assertTrue(package["checks"]["price_numbers_reproducible"])
        self.assertEqual(package["report"]["date"], DAY)

    def test_official_events_require_current_date_and_primary_source(self):
        event = {"primarySource": True, "kind": "policy", "publisher": "海关总署", "publishedAt": DAY, "title": "进境货物检验通知", "sourceUrl": "https://example.gov/notice"}
        report = build_customer_report(DAY, [observation()], official_events=[event, {**event, "primarySource": False}, {**event, "publishedAt": "2026-09-27"}])
        self.assertEqual(len(report["sources"]), 1)
        self.assertIn("海关总署于2026-09-28发布", report["body"])
        self.assertIn("[S1]", report["body"])
        self.assertNotIn("今日无新增政策", report["body"])
        self.assertNotIn("https://", report["body"])

    def test_gate_rejects_unsupported_price(self):
        report = build_customer_report(DAY, [observation()])
        report["body"] = report["body"].replace("5.00美元/公斤", "777.00美元/公斤", 1)
        with self.assertRaises(ValueError):
            validate_customer_report(report, DAY)
        report = build_customer_report(DAY, [observation()])
        report["body"] = report["body"].replace("| 5.00 |", "| 888.00 |", 1)
        with self.assertRaises(ValueError):
            validate_customer_report(report, DAY)


if __name__ == "__main__":
    unittest.main()
