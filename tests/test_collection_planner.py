import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from collection_planner import pending_targets, prioritize_sources


class CollectionPlannerTest(unittest.TestCase):
    def test_only_latest_pending_state_becomes_target(self):
        records = [
            {"country": "LA", "source": "shop-a", "data": {"product_key": "a:1", "platform_id": "shop-a", "species_id": "shiitake", "cross_validation_status": "pending", "candidate_state": "awaiting_recheck", "candidate_attempt": 2}},
            {"country": "LA", "source": "shop-a", "data": {"product_key": "a:1", "platform_id": "shop-a", "species_id": "shiitake", "cross_validation_status": "verified", "candidate_state": "promoted", "candidate_attempt": 1}},
            {"country": "VN", "source": "shop-b", "data": {"product_key": "b:1", "platform_id": "shop-b", "species_id": "oyster_mushroom", "cross_validation_status": "pending", "candidate_state": "deleted_unqualified", "candidate_attempt": 3}},
        ]
        targets = pending_targets(records)
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["product_key"], "a:1")

    def test_recheck_then_independent_channel_are_prioritized(self):
        sources = [
            (object, {"platform": "ordinary", "country": "KZ"}),
            (object, {"platform": "shop-b", "country": "LA", "query_species": "shiitake"}),
            (object, {"platform": "shop-c", "country": "LA"}),
            (object, {"platform": "shop-a", "country": "LA"}),
        ]
        targets = [{"platform": "shop-a", "country": "LA", "species_id": "shiitake", "attempt": 2}]
        ordered = prioritize_sources(sources, targets)
        self.assertEqual([config["platform"] for _, config in ordered], ["shop-a", "shop-b", "shop-c", "ordinary"])


if __name__ == "__main__":
    unittest.main()
