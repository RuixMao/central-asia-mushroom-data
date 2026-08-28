import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from auto_review import resolve_pending_reviews


class AutoReviewLoopTest(unittest.TestCase):
    def test_explained_outlier_is_automatically_resolved(self):
        item = {"validation_status": "needs_review", "review_reasons": ["sanity_outlier"],
                "review_actions": ["check"], "sanity_outlier": True,
                "sanity_review_status": "explained", "sanity_review_reason": "小包装溢价",
                "normalized_quantity_kg": .3, "normalized_price_usd_per_kg": 42.8}
        stats = resolve_pending_reviews([item])
        self.assertEqual(item["validation_status"], "valid")
        self.assertFalse(item["sanity_outlier"])
        self.assertEqual(item["review_decision"], "auto_approve_after_review")
        self.assertEqual(stats["resolved"], 1)

    def test_unverifiable_record_is_quarantined_not_left_pending(self):
        item = {"validation_status": "needs_review", "review_reasons": ["net_weight_missing"],
                "review_actions": ["find_net_weight_on_page_or_package_image"]}
        stats = resolve_pending_reviews([item])
        self.assertEqual(item["validation_status"], "rejected")
        self.assertEqual(item["auto_review_status"], "quarantined")
        self.assertIn("retry_from_source_on_next_scheduled_collection", item["review_actions"])
        self.assertEqual(stats["quarantined"], 1)

    def test_observe_mode_can_preserve_pending(self):
        item = {"validation_status": "needs_review", "review_reasons": ["species_ambiguous"]}
        stats = resolve_pending_reviews([item], quarantine_unresolved=False)
        self.assertEqual(item["validation_status"], "needs_review")
        self.assertEqual(stats["remaining_pending"], 1)


if __name__ == "__main__":
    unittest.main()
