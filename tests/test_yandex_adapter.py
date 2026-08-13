import pathlib, sys, unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from adapters.yandex import YandexMarketAdapter

BASE = {"platform": "yandex-uz", "platform_name": "Yandex Market UZ", "platform_product_id": "search-shampinon",
        "country": "UZ", "city": "Tashkent", "collection_point_id": "TASHKENT_POINT_01",
        "url": "https://market.yandex.uz/search?text=шампиньоны", "title": "Шампиньоны свежие",
        "package": "1 kg", "currency": "UZS", "language": "ru"}


def rendered_body():
    """模拟浏览器渲染后的 body 文本（含商品标题与价格）。"""
    return ("Каталог товаров Шампиньоны — купить по низкой цене на Market Yandex Go\n"
            "Шампиньоны свежие 500 г\n50 000 сум\nв корзину\n"
            "Шампиньоны консервированные 300 г\n18 500 сум\n"
            "Вешенки свежие 1 кг\n42 000 сум")


class YandexMarketAdapterTest(unittest.TestCase):
    def test_parse_rendered_finds_first_mushroom_price(self):
        adapter = YandexMarketAdapter(BASE)
        row, error = adapter.parse_rendered("<html></html>", rendered_body())
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 50000.0)
        self.assertIn("Шампиньоны", row["original_title"])
        self.assertIn("50 000 сум", row["raw_price_text"])

    def test_price_missing(self):
        adapter = YandexMarketAdapter(BASE)
        row, error = adapter.parse_rendered("<html></html>", "Ничего не найдено на этой странице")
        self.assertIsNone(row)
        self.assertEqual(error, "price_missing")

    def test_zero_price_skipped(self):
        adapter = YandexMarketAdapter(BASE)
        body = "Грибы шампиньоны 0 сум какой-то товар"
        row, error = adapter.parse_rendered("<html></html>", body)
        self.assertEqual(error, "price_missing")

    def test_collect_wraps_render_error(self):
        with patch("adapters.yandex.YandexMarketAdapter.render", return_value=(None, "render_failed")):
            row, error = YandexMarketAdapter(BASE).collect()
        self.assertIsNone(row)
        self.assertEqual(error, "render_failed")

    def test_parse_rendered_many_all_products(self):
        """多商品：返回所有【含菌词+价格】片段，且每条有唯一 platform_product_id。"""
        rows = YandexMarketAdapter(BASE).parse_rendered_many("<html></html>", rendered_body())
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["current_price"], 50000.0)
        self.assertTrue(all(row["platform_product_id"].startswith("yandex-uz-") for row in rows))
        self.assertEqual(len({row["platform_product_id"] for row in rows}),3)
        titles = {r["original_title"] for r in rows}
        self.assertTrue(any("Вешенки" in t for t in titles))


if __name__ == "__main__":
    unittest.main()
