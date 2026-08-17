import pathlib, sys, unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.lochin import LochinAdapter
from adapters.makro import MakroAdapter
from adapters.olx import OlxAdapter, OlxSearchAdapter
from adapters.somon import SomonAdapter
from adapters.yukber import YukberAdapter

ROOT = pathlib.Path(__file__).parent / "fixtures"


class Response:
    def __init__(self, text, url="https://example.test/"):
        self.text = text
        self.content = text.encode()
        self.url = url


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


class UzbekistanExpansionTest(unittest.TestCase):
    COMMON = {"country": "UZ", "city": "Tashkent", "collection_point_id": "TASHKENT_POINT_01",
              "currency": "UZS", "language": "ru", "package": "1 kg"}

    def test_lochin_server_html(self):
        config = {**self.COMMON, "platform": "lochin-uz", "platform_name": "Lochin",
                  "platform_product_id": "7057", "url": "https://lochin.uz/product/7057",
                  "title": "Грибы шампиньоны, вес", "marker": "Грибы шампиньоны, вес"}
        html = "<html><title>Грибы шампиньоны, вес - Lochin</title><body><h1>Грибы шампиньоны, вес</h1><b>100,000 сум</b></body></html>"
        row, error = collect(LochinAdapter, config, html)
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 100000)

    def test_yukber_server_html(self):
        config = {**self.COMMON, "platform": "yukber-uz", "platform_name": "Yukber",
                  "platform_product_id": "YK1820", "url": "https://yukber.uz/uz/YK1820_uz",
                  "title": "Qo'ziqorin Shampinyon 1kg"}
        html = "<html><title>Qo'ziqorin Shampinyon 1kg</title><body><h1>Qo'ziqorin Shampinyon 1kg</h1><span>92,990 UZS</span></body></html>"
        row, error = collect(YukberAdapter, config, html)
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 92990)

    def test_olx_search_filters_growing_supplies(self):
        config = {**self.COMMON, "platform": "olx-uz", "platform_name": "OLX.uz",
                  "platform_product_id": "search", "url": "https://www.olx.uz/list/q-грибы/",
                  "title": "Грибы", "package": ""}
        html = """<div><div><a href='/d/obyavlenie/griby-veshenki-svezhie-1-kg-IDabc1.html'>
        Грибы вешенки свежие 1 kg</a><span>25 000 сум</span></div></div>
        <div><div><a href='/d/obyavlenie/semena-veshenki-IDabc2.html'>Семена грибов вешенки</a>
        <span>15 000 сум</span></div></div>"""
        with patch("adapters.olx.safe_get", return_value=Response(html, config["url"])):
            rows, error = OlxSearchAdapter(config).collect_many()
        self.assertIsNone(error)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["platform_product_id"], "IDabc1")

    def test_makro_api_excludes_mushroom_flavoured_prepared_food(self):
        class JsonResponse(Response):
            def json(self):
                return {"results": [
                    {"id": 1, "title": "KUNCEVO OQ QO‘ZIQORINLI KARTOSHKA PYURESI 40GR", "newPrice": 8450},
                    {"id": 2, "title": "Qo‘ziqorin shampinyon 500 g", "newPrice": 32000},
                ]}
        config = {**self.COMMON, "platform": "makro-uz", "platform_name": "Makro",
                  "platform_product_id": "scan", "url": "https://makromarket.uz/catalog", "title": "catalog"}
        with patch("adapters.makro.safe_get", return_value=JsonResponse("{}")):
            rows, error = MakroAdapter(config).collect_many()
        self.assertIsNone(error)
        self.assertEqual([row["platform_product_id"] for row in rows], ["2"])


if __name__ == "__main__":
    unittest.main()
