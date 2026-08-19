import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.lochin import LochinAdapter
from adapters.somon import SomonAdapter
from adapters.yukber import YukberAdapter
from taxonomy import classify, normalize_price, parse_package


class Response:
    def __init__(self, text):
        self.text = text
        self.content = text.encode("utf-8")


class PriceEvidenceTest(unittest.TestCase):
    def test_volume_is_not_converted_to_mass(self):
        parsed = parse_package("Qo'ziqorin вешенки 1L")
        self.assertEqual(parsed["parse_status"], "volume_not_mass")
        self.assertIsNone(parsed["quantity_kg"])

    def test_volume_can_use_explicit_one_litre_one_kg_policy(self):
        result = normalize_price(250, "425 ml", allow_volume=True, volume_kg_per_l=1.0)
        self.assertEqual(result["parse_status"], "valid_volume_estimate")
        self.assertEqual(result["quantity_kg"], 0.425)
        self.assertEqual(result["price_per_kg"], 588.24)
        self.assertEqual(result["conversion_basis"], "1 L = 1 kg")

    def test_somon_description_changes_form_to_dried(self):
        html = '''<html><head><meta property="og:title" content="Грибы шампиньоны 10 c.">
        <meta name="description" content="Шампиньони хушккардаи аслӣ"></head></html>'''
        row, error = SomonAdapter({"package": "", "url": "https://example.test"}).parse(Response(html))
        self.assertIsNone(error)
        result = classify(row["original_title"], description=row["description"])
        self.assertEqual(result["product_form"], "dried")
        self.assertEqual(parse_package(row["original_title"])["parse_status"], "invalid")

    def test_yukber_prefers_visible_heading_with_litre_unit(self):
        html = '''<html><head><title>旧标题 1kg</title></head><body>
        <h1>Qo'ziqorin вешенки (1l)</h1><div>20,990 UZS</div></body></html>'''
        row, error = YukberAdapter({"package": "1 l", "url": "https://example.test"}).parse(Response(html))
        self.assertIsNone(error)
        self.assertIn("1l", row["original_title"])
        self.assertEqual(parse_package(row["original_title"])["parse_status"], "volume_not_mass")

    def test_weighted_lochin_item_without_unit_has_no_mass_evidence(self):
        html = '''<html><head><title>商品 - Lochin</title></head><body>
        <h1>Грибы Вешенки, вес</h1><div>55,000 сум</div></body></html>'''
        row, error = LochinAdapter({"marker": "Грибы Вешенки, вес", "package": "", "url": "https://example.test"}).parse(Response(html))
        self.assertIsNone(error)
        self.assertEqual(parse_package(row["original_title"])["parse_status"], "invalid")


if __name__ == "__main__":
    unittest.main()
