"""中亚高频野生菌覆盖测试:taxonomy 分类 + 检索词矩阵。"""
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))

from taxonomy import classify
from search_queries import COUNTRY_SEARCH_TERMS


class TestWildSpeciesTaxonomy(unittest.TestCase):
    def test_central_asia_wild_species_covered(self):
        """中亚高频野生菌(羊肚菌/牛肝菌/鸡油菌/蜜环菌/松乳菌/乳菇/蓝柄菇)应可分类。"""
        cases = {
            "Грибы рыжики солёные 500 г": "saffron_milk_cap",
            "Грузди маринованные 1 кг": "milk_mushroom",
            "Синеножка свежая 300 г": "blewit",
            "Сморчки сушёные 100 г": "morel",
            "Лисички жареные 250 г": "chanterelle",
            "Опята маринованные 400 г": "honey_fungus",
            "Маслята замороженные 500 г": "suillus",
            "Белые грибы сушёные 200 г": "porcini",
        }
        for title, want in cases.items():
            c = classify(title, language="ru")
            self.assertEqual(c["status"], "classified", f"{title} -> {c['status']}")
            self.assertEqual(c["species_id"], want, f"{title} -> {c['species_id']}, want {want}")

    def test_wild_species_in_search_matrix(self):
        """五国检索矩阵都应含野生菌检索词(expanded 模式才能逐菌种扫)。"""
        wild = {"morel", "porcini", "chanterelle", "honey_fungus", "suillus",
                "saffron_milk_cap", "milk_mushroom", "blewit"}
        for country in ("KZ", "UZ", "KG", "TJ", "TM"):
            species = set()
            for lang in COUNTRY_SEARCH_TERMS[country].values():
                species.update(lang.keys())
            self.assertTrue(wild <= species, f"{country} 缺野生菌: {wild - species}")

    def test_expanded_mode_includes_wild(self):
        """expanded 模式下 fetch_price 的 SOURCES 应覆盖全部野生菌检索任务。"""
        import os
        os.environ["SEARCH_QUERY_MODE"] = "expanded"
        try:
            import importlib
            import fetch_price as fp
            importlib.reload(fp)
            species = {c.get("query_species") for _, c in fp.SOURCES if c.get("query_species")}
            for want in ("morel", "porcini", "chanterelle", "honey_fungus",
                         "saffron_milk_cap", "milk_mushroom", "blewit"):
                self.assertIn(want, species, f"expanded 模式缺 {want}")
        finally:
            os.environ.pop("SEARCH_QUERY_MODE", None)


if __name__ == "__main__":
    unittest.main()
