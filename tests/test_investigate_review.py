import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from investigate_review import investigate_record


class Response:
    text = '''<html><head><script type="application/ld+json">
    {"@type":"Product","name":"Грибы шампиньоны","description":"упаковка 500 г"}
    </script></head></html>'''


class TargetedInvestigationTest(unittest.TestCase):
    def test_missing_weight_is_retrieved_and_record_passes_second_review(self):
        item = {"validation_status":"needs_review", "review_reasons":["net_weight_missing"],
                "product_url":"https://example.test/product", "original_title":"Грибы шампиньоны",
                "original_category":"", "original_language":"ru", "country":"KZ",
                "species_id":"button_mushroom", "product_form":"fresh",
                "classification_status":"classified", "classification_confidence":.98,
                "current_price":1000, "usd_rate_local_per_usd":500}
        self.assertTrue(investigate_record(item, fetcher=lambda _: Response()))
        self.assertEqual(item["validation_status"], "valid")
        self.assertEqual(item["normalized_quantity_kg"], .5)
        self.assertEqual(item["package_source"], "page_recheck")
        self.assertEqual(item["investigation_status"], "resolved")

    def test_unavailable_page_does_not_get_guessed(self):
        item = {"validation_status":"needs_review", "review_reasons":["net_weight_missing"],
                "product_url":"https://example.test/product"}
        self.assertFalse(investigate_record(item, fetcher=lambda _: None))
        self.assertEqual(item["investigation_status"], "source_unavailable")


if __name__ == "__main__":
    unittest.main()
