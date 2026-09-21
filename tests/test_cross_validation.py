import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from cross_validation import cross_validate_prices


def item(platform="shop-a", price=10, **overrides):
    base = {"country": "LA", "platform": platform, "collection_point_id": "VTE", "platform_product_id": "sku-1",
            "product_url": "https://example.test/item", "species_id": "oyster_mushroom", "product_form": "fresh",
            "normalized_price_usd_per_kg": price, "validation_status": "valid"}
    return {**base, **overrides}


class CrossValidationTest(unittest.TestCase):
    def test_first_observation_stays_out_of_customer_pool(self):
        row = item()
        stats = cross_validate_prices([row], [])
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(row["validation_status"], "needs_review")
        self.assertEqual(row["cross_validation_status"], "pending")
        self.assertEqual(row["verification_score"], 40)

    def test_repeat_observation_verifies_price(self):
        row = item()
        history = [{"country": "LA", "source": "shop-a", "data": {"status": "live", "product_key": "shop-a:VTE:sku-1",
                    "platform_id": "shop-a", "species_id": "oyster_mushroom", "product_form": "fresh",
                    "normalized_price_usd_per_kg": 10.5, "observed_at": "2026-09-20"}}]
        stats = cross_validate_prices([row], history)
        self.assertEqual(stats["verified"], 1)
        self.assertEqual(row["validation_status"], "valid")
        self.assertEqual(row["verification_score"], 70)
        self.assertIn("repeat_observation", {entry["type"] for entry in row["verification_evidence"]})

    def test_independent_channel_verifies_both_prices(self):
        rows = [item("shop-a", 10), item("shop-b", 12, platform_product_id="sku-2")]
        stats = cross_validate_prices(rows, [])
        self.assertEqual(stats["verified"], 2)
        self.assertTrue(all(row["cross_validation_status"] == "verified" for row in rows))

    def test_extreme_peer_does_not_validate(self):
        rows = [item("shop-a", 2), item("shop-b", 20, platform_product_id="sku-2")]
        stats = cross_validate_prices(rows, [])
        self.assertEqual(stats["pending"], 2)

    def test_third_party_anchor_is_identified_as_independent_evidence(self):
        row = item()
        history = [{"country": "LA", "source": "industry-audit", "data": {"status": "live", "product_key": "audit:1",
                    "platform_id": "industry-audit", "species_id": "oyster_mushroom", "product_form": "fresh",
                    "normalized_price_usd_per_kg": 11, "observed_at": "2026-09-20", "grade": "C",
                    "source_type": "third_party_audit"}}]
        cross_validate_prices([row], history)
        self.assertIn("third_party_anchor", {entry["type"] for entry in row["verification_evidence"]})
        self.assertEqual(row["cross_validation_status"], "verified")


if __name__ == "__main__":
    unittest.main()
