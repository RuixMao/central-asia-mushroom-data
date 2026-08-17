import json
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.catalog_search import CatalogSearchAdapter
from adapters.wildberries import WildberriesAdapter
from adapters.flagma import FlagmaAdapter


BASE = {"platform": "shop", "platform_name": "Shop", "platform_product_id": "search",
        "country": "KG", "city": "Bishkek", "collection_point_id": "BISHKEK_POINT_01",
        "url": "https://shop.test/search?q=грибы", "title": "Каталог", "package": "",
        "currency": "KGS", "language": "ru"}


class Response:
    def __init__(self, text, url="https://shop.test/search"):
        self.text = text
        self.content = text.encode()
        self.url = url
    def json(self):
        return json.loads(self.text)


class CatalogExpansionTest(unittest.TestCase):
    def test_jsonld_collects_multiple_food_products(self):
        html = '''<script type="application/ld+json">{"@type":"ItemList","itemListElement":[
        {"@type":"Product","sku":"a1","name":"Шампиньоны свежие 500 г","url":"/a1","offers":{"price":260}},
        {"@type":"Product","sku":"a2","name":"Вешенки 1 кг","url":"/a2","offers":{"price":310}},
        {"@type":"Product","sku":"a3","name":"Мицелий вешенки","url":"/a3","offers":{"price":90}}]}</script>'''
        with patch("adapters.catalog_search.safe_get", return_value=Response(html)):
            rows, error = CatalogSearchAdapter(BASE).collect_many()
        self.assertIsNone(error)
        self.assertEqual([r["platform_product_id"] for r in rows], ["a1", "a2"])

    def test_wildberries_price_units_and_ids(self):
        payload = {"data": {"products": [{"id": 12, "name": "Шампиньоны 400 г", "salePriceU": 129900}]}}
        config = {**BASE, "platform": "wildberries-kg", "dest": "verified"}
        with patch("adapters.wildberries.safe_get", return_value=Response(json.dumps(payload))):
            rows, error = WildberriesAdapter(config).collect_many()
        self.assertIsNone(error)
        self.assertEqual(rows[0]["platform_product_id"], "12")
        self.assertEqual(rows[0]["current_price"], 1299)

    def test_wildberries_failure_is_gap_not_zero(self):
        config = {**BASE, "platform": "wildberries-kg", "dest": "verified"}
        with patch("adapters.wildberries.safe_get", return_value=None):
            rows, error = WildberriesAdapter(config).collect_many()
        self.assertEqual(rows, [])
        self.assertEqual(error, "rate_limited_or_no_products")

    def test_flagma_price_on_request_is_gap(self):
        html = '<article><a href="/offer/1">Шампиньоны свежие оптом</a><span>Цена договорная</span></article>'
        with patch("adapters.flagma.safe_get", return_value=Response(html)):
            rows, error = FlagmaAdapter(BASE).collect_many()
        self.assertEqual(rows, [])
        self.assertEqual(error, "price_on_request")


if __name__ == "__main__":
    unittest.main()
