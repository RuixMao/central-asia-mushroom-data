import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.next_data import NextDataProductAdapter


class NextDataAdapterTest(unittest.TestCase):
    def test_parses_embedded_mushroom_product(self):
        adapter = NextDataProductAdapter({"url": "https://shop.test/th/product/item", "currency": "THB"})
        html = '<script id="__NEXT_DATA__" type="application/json">{"props":{"product":{"sku":"23886552","name":"เห็ดออรินจิ","urlKey":"eryngii","weightPerPiece":0.2,"finalPricePerUOW":25,"stockStatus":"IN_STOCK"}}}</script>'
        rows, error = adapter.parse_html(html)
        self.assertIsNone(error)
        self.assertEqual(rows[0]["current_price"], 25)
        self.assertEqual(rows[0]["package"], "0.2 kg")
        self.assertTrue(rows[0]["detail_verified"])


if __name__ == "__main__":
    unittest.main()
