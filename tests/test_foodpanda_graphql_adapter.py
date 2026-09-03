import unittest
from unittest.mock import patch

from adapters.foodpanda_graphql import FoodpandaGraphQLAdapter, FoodpandaPrimaryFallbackAdapter


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

    @patch("adapters.foodpanda_graphql.requests.get")
    def test_discovers_category_ids_for_cambodia(self, get):
        get.return_value.text = '/category/4908d63c-388a-43f4-9866-3ae2a936cc6a'
        get.return_value.raise_for_status.return_value = None
        config = {"url": "https://www.foodpanda.com.kh/en/shop/bq32/lucky", "vendor_code": "bq32"}
        self.assertEqual(["4908d63c-388a-43f4-9866-3ae2a936cc6a"], FoodpandaGraphQLAdapter(config)._category_ids())

    @patch("adapters.foodpanda_graphql.requests.get")
    def test_parses_server_rendered_storefront_as_api_fallback(self, get):
        get.return_value.content = b'''<article data-testid="groceries-product-card-9046521" data-id="product-9046521">
          <p data-testid="groceries-product-card-name">LUCKY MUSHROOM ENOKI 200G</p>
          <span data-testid="groceries-product-card-price">$ 0.76</span>
        </article>'''
        get.return_value.text = get.return_value.content.decode()
        get.return_value.raise_for_status.return_value = None
        adapter = FoodpandaPrimaryFallbackAdapter({**self.config, "currency": "USD"})
        rows = adapter._storefront_rows()
        self.assertEqual(1, len(rows))
        self.assertEqual("9046521", rows[0]["platform_product_id"])
        self.assertEqual("200 g", rows[0]["package"])
        self.assertEqual(0.76, rows[0]["current_price"])
        self.assertEqual("foodpanda_storefront_html", rows[0]["source_type"])


if __name__ == "__main__":
    unittest.main()
