import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from review import review_record


def record(**overrides):
    base = {
        "classification_status": "classified",
        "classification_confidence": 0.98,
        "species_id": "button_mushroom",
        "package_source": "page_title",
        "normalized_quantity_kg": 0.5,
        "current_price": 100,
    }
    return {**base, **overrides}


class AutomatedReviewTest(unittest.TestCase):
    def test_complete_deterministic_evidence_is_approved(self):
        self.assertEqual(review_record(record())["decision"], "auto_approve")

    def test_missing_weight_stays_in_manual_review(self):
        result = review_record(record(package_source="unverified", normalized_quantity_kg=None))
        self.assertEqual(result["validation_status"], "needs_review")
        self.assertIn("net_weight_missing", result["reasons"])

    def test_volume_with_explicit_market_conversion_is_approved(self):
        result = review_record(record(
            package_source="page_title_volume_estimate",
            package_conversion_basis="1 L = 1 kg",
        ))
        self.assertEqual(result["decision"], "auto_approve")

    def test_volume_without_conversion_basis_stays_in_review(self):
        result = review_record(record(package_source="page_title_volume_estimate"))
        self.assertIn("volume_conversion_missing", result["reasons"])

    def test_ambiguous_species_stays_in_manual_review(self):
        result = review_record(record(classification_status="ambiguous", species_id=None, classification_confidence=0.5))
        self.assertIn("species_ambiguous", result["reasons"])

    def test_excluded_product_is_rejected(self):
        result = review_record(record(classification_status="excluded"))
        self.assertEqual(result["decision"], "auto_reject")


if __name__ == "__main__":
    unittest.main()
