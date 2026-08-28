import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from fetch_laos_retail_fallback import build_items


class LaosRetailFallbackTest(unittest.TestCase):
    def test_missing_package_listing_is_not_normalized_per_kg(self):
        item = build_items(22000)[0]
        self.assertEqual(item["species_id"], "enoki")
        self.assertEqual(item["current_price"], 15000)
        self.assertIsNone(item["normalized_price_per_kg"])
        self.assertIn("relaxed_missing_package", item["review_reasons"][0])


if __name__ == "__main__":
    unittest.main()
