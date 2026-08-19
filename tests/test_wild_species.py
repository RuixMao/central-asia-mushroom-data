"""中亚高频野生菌覆盖测试:taxonomy 分类 + 检索词矩阵。"""
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))

from taxonomy import classify
from search_queries import COUNTRY_SEARCH_TERMS, iter_country_queries


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

    def test_steppe_mushroom_ferula(self):
        """阿魏菇/白灵菇/草原白蘑菇(用户提供:荒漠原生珍稀菌)应分类为 steppe_mushroom,
        且与杏鲍菇(king_oyster)、平菇(oyster)不冲突。"""
        cases = {
            "Белый степной гриб свежий 500 г": "steppe_mushroom",
            "阿魏菇 500克": "steppe_mushroom",
            "白灵菇 干品 200克": "steppe_mushroom",
            "Королевская вешенка 1 кг": "king_oyster_mushroom",
            "Грибы вешенки свежие": "oyster_mushroom",
        }
        for title, want in cases.items():
            lang = "zh" if any(ch >= "\u4e00" for ch in title) else "ru"
            c = classify(title, language=lang)
            self.assertEqual(c["species_id"], want, f"{title} -> {c['species_id']}, want {want}")

    def test_broad_white_mushroom_terms_need_review(self):
        """本地语“白蘑菇”不能独自区分牛肝菌和阿魏菇。"""
        for title, language in (("Ак козу карын 300 г", "ky"), ("Oq qo'ziqorin 300 g", "uz"), ("Ферула 300 г", "ru")):
            c = classify(title, language=language)
            self.assertNotEqual(c["status"], "classified", f"{title} 不应被强制分类")

    def test_steppe_mushroom_in_search_matrix(self):
        """五国检索矩阵都应含阿魏菇检索词。"""
        for country in ("KZ", "UZ", "KG", "TJ", "TM"):
            species = set()
            for lang in COUNTRY_SEARCH_TERMS[country].values():
                species.update(lang.keys())
            self.assertIn("steppe_mushroom", species, f"{country} 缺阿魏菇")

    def test_deduped_queries_still_emit_every_species(self):
        """矩阵中的每个品类在跨语言去重后仍必须至少发出一个查询。"""
        for country in ("KZ", "UZ", "KG", "TJ", "TM"):
            configured = {
                species_id
                for language_terms in COUNTRY_SEARCH_TERMS[country].values()
                for species_id in language_terms
            }
            emitted = {query.species_id for query in iter_country_queries(country, configured)}
            self.assertEqual(configured, emitted, f"{country} 去重后丢失: {configured - emitted}")

    def test_no_term_maps_to_multiple_species_in_one_language(self):
        """同一国家、同一语言的主检索词不得指向两个品类。"""
        for country, languages in COUNTRY_SEARCH_TERMS.items():
            for language, species_terms in languages.items():
                owners = {}
                for species_id, terms in species_terms.items():
                    for term, _origin in terms:
                        key = term.casefold()
                        self.assertNotIn(key, owners, f"{country}/{language} {term} 同时属于 {owners.get(key)} 和 {species_id}")
                        owners[key] = species_id


if __name__ == "__main__":
    unittest.main()
