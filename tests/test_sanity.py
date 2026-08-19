import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from sanity import apply_sanity_validation, check_usd_per_kg, review_sanity_outliers, sanity_band


class PriceSanityTest(unittest.TestCase):
    def test_kg_button_mushroom_outlier_is_marked(self):
        result = check_usd_per_kg("button_mushroom", "KG", 42.84)
        self.assertTrue(result["sanity_outlier"])
        self.assertEqual(result["sanity_reason"], "超出合理区间(2~20 USD/kg)")
        merged = apply_sanity_validation({"decision": "auto_approve", "validation_status": "valid", "reasons": [], "actions": []}, "button_mushroom", "KG", 42.84)
        self.assertEqual(merged["validation_status"], "needs_review")
        self.assertTrue(merged["sanity_outlier"])

    def test_kg_button_mushroom_normal_price_remains_valid(self):
        result = check_usd_per_kg("button_mushroom", "KG", 5.92)
        self.assertFalse(result["sanity_outlier"])
        self.assertIsNone(result["sanity_reason"])
        merged = apply_sanity_validation({"decision": "auto_approve", "validation_status": "valid", "reasons": [], "actions": []}, "button_mushroom", "KG", 5.92)
        self.assertEqual(merged["validation_status"], "valid")

    def test_species_and_fallback_bands(self):
        self.assertEqual(sanity_band("oyster_mushroom", "KZ"), (1.0, 15.0))
        self.assertEqual(sanity_band("shiitake", "UZ"), (5.0, 40.0))
        self.assertEqual(sanity_band("unknown", "TM"), (1.0, 50.0))

    def test_small_package_outlier_is_explained_but_stays_in_review(self):
        items = [
            {"country": "KG", "species_id": "button_mushroom", "product_form": "fresh",
             "normalized_quantity_kg": 0.3, "normalized_price_usd_per_kg": 42.84,
             "validation_status": "needs_review", "sanity_outlier": True,
             "sanity_reason": "超出合理区间(2~20 USD/kg)"},
            {"country": "KG", "species_id": "button_mushroom", "product_form": "fresh",
             "normalized_quantity_kg": 1.0, "normalized_price_usd_per_kg": 5.92,
             "validation_status": "valid", "sanity_outlier": False},
        ]
        self.assertEqual(review_sanity_outliers(items), 1)
        self.assertEqual(items[0]["validation_status"], "needs_review")
        self.assertEqual(items[0]["sanity_review_status"], "explained")
        self.assertIn("300g小包装", items[0]["sanity_review_reason"])
        self.assertIn("1000g包装", items[0]["sanity_review_reason"])
        self.assertIn("最大可能因素", items[0]["sanity_review_reason"])
        self.assertNotIn("可解释因素", items[0]["sanity_review_reason"])
        self.assertEqual(items[1]["validation_status"], "valid")


if __name__ == "__main__":
    unittest.main()
