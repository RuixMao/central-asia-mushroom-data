import unittest
from unittest.mock import patch

from adapters.foodpanda_graphql import FoodpandaGraphQLAdapter


class FakeResponse:
    content = b"catalog"

    def raise_for_status(self):
        return None

    def json(self):
        return {"data": {"groceryCategoryDetailsPage": {"components": {"listingComponents": [
            {"items": [
                {"id": "1", "name": "Enoki Mushroom 100g", "price": 15000, "isAvailable": True, "attributes": {"contentsWeightInfo": {"unit": "GRAM", "value": 100}}},
                {"id": "2", "name": "White Shimeji Mushroom", "price": 18000, "isAvailable": True, "attributes": {"contentsWeightInfo": {"unit": "PACKETS", "value": 1}}},
                {"id": "3", "name": "Mushroom Growing Kit", "price": 99000, "attributes": {}},
            ]}
        ]}}}}


class FoodpandaGraphQLAdapterTest(unittest.TestCase):
    def setUp(self):
        self.config = {"platform": "foodpanda-api-champa-la", "url": "https://www.foodpanda.la/en/shop/s8f0/champa-market", "vendor_code": "s8f0", "category_id": "fresh", "currency": "LAK"}

    @patch("adapters.foodpanda_graphql.requests.post", return_value=FakeResponse())
    def test_parses_mushrooms_and_preserves_packet_quote(self, _post):
        rows, error = FoodpandaGraphQLAdapter(self.config).collect_many()
        self.assertIsNone(error)
        self.assertEqual(2, len(rows))
        self.assertEqual("100 g", rows[0]["package"])
        self.assertEqual("1 packet", rows[1]["package"])
        self.assertEqual("foodpanda_graphql_catalog", rows[0]["source_type"])


if __name__ == "__main__":
    unittest.main()
