import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))
from adapters.kaspi import KaspiAdapter

ROOT = pathlib.Path(__file__).parent / "fixtures"
BASE = {"platform": "kaspi-kz", "platform_product_id": "search-shampinon",
        "url": "https://kaspi.kz/shop/search/?text=шампиньон", "package": "500 g"}


class KaspiTest(unittest.TestCase):
    def test_rendered_fixture(self):
        row, error = KaspiAdapter(BASE).parse_rendered((ROOT / "kaspi_search_rendered.html").read_text(encoding="utf-8"))
        self.assertIsNone(error)
        self.assertEqual(row["current_price"], 1590)
        self.assertIn("10001", row["url"])

    def test_missing_is_gap(self):
        row, error = KaspiAdapter({"url": "x"}).parse_rendered("<main>Нет товаров</main>")
        self.assertIsNone(row)
        self.assertEqual(error, "price_missing")

    def test_parse_rendered_many_all_mushrooms(self):
        """多商品：返回所有含菌词+价格的卡片，过滤非蘑菇，且每条有唯一 platform_product_id。"""
        rows = KaspiAdapter(BASE).parse_rendered_many((ROOT / "kaspi_search_rendered.html").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 3)  # 苹果被过滤
        titles = [r["original_title"] for r in rows]
        self.assertTrue(any("1 кг" in t for t in titles))
        ids = {r["platform_product_id"] for r in rows}
        self.assertEqual(len(ids), 3)  # search-shampinon-10001/10002/10003 各不相同
        self.assertIn("kaspi-10001", ids)
        self.assertTrue(all(r["current_price"] > 0 for r in rows))

    def test_collect_many_wraps_render_error(self):
        from unittest.mock import patch
        with patch("adapters.kaspi.KaspiAdapter.render", return_value=(None, "render_failed")):
            rows, error = KaspiAdapter(BASE).collect_many()
        self.assertEqual(rows, [])
        self.assertEqual(error, "render_failed")


if __name__ == "__main__":
    unittest.main()
