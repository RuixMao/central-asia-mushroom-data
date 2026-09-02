import json
import unittest

from adapters.makro_pro import MakroProAdapter


class MakroProAdapterTest(unittest.TestCase):
    def test_parses_embedded_catalog_and_filters_non_food(self):
        payload = {
            "props": {"pageProps": {"initialSearchResult": {"hits": [
                {"document": {"productId": "p1", "makroId": "861406", "searchTitle": {"EN": "Enoki Mushroom 1 kg"}, "displayPrice": 57, "originalPrice": 60, "inStock": 1}},
                {"document": {"productId": "p2", "makroId": "861407", "titleEn": "Wood Ear Mushroom 200 g", "displayPrice": "27.00", "inStock": 1}},
                {"document": {"productId": "p3", "titleEn": "Mushroom Growing Kit", "displayPrice": 99}},
            ]}}}
        }
        html = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script>'
        adapter = MakroProAdapter({"platform": "makro-pro-th", "currency": "THB"})
        rows, error = adapter.parse_html(html, "https://www.makro.pro/en/c/test")
        self.assertIsNone(error)
        self.assertEqual(2, len(rows))
        self.assertEqual(57.0, rows[0]["current_price"])
        self.assertEqual("embedded_catalog_json", rows[0]["source_type"])
        self.assertEqual("https://www.makro.pro/en/p/861406-p1", rows[0]["url"])
        self.assertEqual(60.0, rows[0]["original_price"])

    def test_reports_missing_next_payload(self):
        adapter = MakroProAdapter({"platform": "makro-pro-mm", "currency": "MMK"})
        rows, error = adapter.parse_html("<html></html>", "https://example.com")
        self.assertEqual([], rows)
        self.assertEqual("next_data_missing", error)


if __name__ == "__main__":
    unittest.main()
