import unittest
from unittest.mock import patch

from adapters.bachhoaxanh import BachHoaXanhAdapter


class Response:
    content = b"bhx"
    def raise_for_status(self): pass
    def json(self):
        return {"data": {"products": [{"id": 1, "fullName": "Nấm bào ngư xám 300g", "url": "/nam-tuoi/nam-bao-ngu", "unit": "300g", "productPrices": [{"price": 22000}]}]}}


class BachHoaXanhAdapterTest(unittest.TestCase):
    @patch("adapters.bachhoaxanh.requests.get", return_value=Response())
    def test_api_primary_returns_mushroom_price(self, _get):
        config = {"url": "https://www.bachhoaxanh.com/nam-tuoi/", "currency": "VND", "platform": "bach-hoa-xanh-vn"}
        rows, error = BachHoaXanhAdapter(config).collect_many()
        self.assertIsNone(error)
        self.assertEqual(22000, rows[0]["current_price"])
        self.assertEqual("bachhoaxanh_api", rows[0]["source_type"])


if __name__ == "__main__":
    unittest.main()
