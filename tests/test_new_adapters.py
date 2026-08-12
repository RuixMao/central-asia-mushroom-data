import pathlib, sys, unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.olx import OlxAdapter
from adapters.somon import SomonAdapter

ROOT = pathlib.Path(__file__).parent / "fixtures"


class Response:
    def __init__(self, text):
        self.text = text
        self.content = text.encode()


def html_of(name):
    return (ROOT / name).read_text(encoding="utf-8", errors="ignore")


def collect(adapter_cls, config, html):
    with patch("adapters.base.safe_get", return_value=Response(html)):
        return adapter_cls(config).collect()


class OlxAdapterTest(unittest.TestCase):
    BASE = {"platform": "olx-uz", "platform_name": "OLX.uz", "platform_product_id": "p1",
            "country": "UZ", "city": "Tashkent", "collection_point_id": "TASHKENT_POINT_01",
            "url": "https://www.olx.uz/d/obyavlenie/x.html", "title": "Шампиньоны в ящиках",
            "package": "1 box", "currency": "UZS", "language": "ru"}

    def test_real_fixture_price(self):
        row, error = collect(OlxAdapter, self.BASE, html_of("olx_shampinon.html"))
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 65000.0)
        self.assertIn("Шампиньоны", row["original_title"])
        self.assertIn("сум", row["raw_price_text"].lower())

    def test_missing_price(self):
        row, error = collect(OlxAdapter, self.BASE, "<html><title>Товар без цены</title></html>")
        self.assertIsNone(row)
        self.assertEqual(error, "price_missing")

    def test_zero_price_rejected(self):
        row, error = collect(OlxAdapter, self.BASE, '<html><meta property="og:title" content="Грибы 0 сум"/></html>')
        self.assertIsNone(row)
        self.assertEqual(error, "zero_price")


class SomonAdapterTest(unittest.TestCase):
    BASE = {"platform": "somon", "platform_name": "Somon.tj", "platform_product_id": "15687107",
            "country": "TJ", "city": "Dushanbe", "collection_point_id": "DUSHANBE_POINT_01",
            "url": "https://somon.tj/adv/15687107_griby-shampinon/", "title": "Грибы шампиньоны",
            "package": "1 kg", "currency": "TJS", "language": "ru"}

    def test_real_fixture_price(self):
        row, error = collect(SomonAdapter, self.BASE, html_of("somon_shampinon.html"))
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 10.0)
        self.assertIn("шампиньоны", row["original_title"].lower())
        self.assertIn("10 c.", row["raw_price_text"])

    def test_missing_price(self):
        row, error = collect(SomonAdapter, self.BASE, "<html><title>Шампиньоны свежие</title></html>")
        self.assertIsNone(row)
        self.assertEqual(error, "price_missing")

    def test_zero_price_rejected(self):
        row, error = collect(SomonAdapter, self.BASE, '<html><meta property="og:title" content="Грибы 0 c."/></html>')
        self.assertIsNone(row)
        self.assertEqual(error, "zero_price")


if __name__ == "__main__":
    unittest.main()
