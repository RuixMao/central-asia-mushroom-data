import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))

from search_queries import iter_country_queries, COUNTRY_SEARCH_TERMS
from taxonomy import classify, EXCLUDE_ONLY
from adapters.kaspi import NON_FOOD as KASPI_NON_FOOD

# ── ① 词源标注 ─────────────────────────────────────────────────────────

def test_search_query_has_origin():
    queries = list(iter_country_queries("KZ"))
    for q in queries:
        assert q.term_origin in ("native", "loan", "russian")

def test_kazakh_generic_is_native():
    kk_mush = [q for q in iter_country_queries("KZ") if q.language == "kk" and q.species_id == "mushrooms"]
    assert kk_mush and kk_mush[0].term_origin == "native"
    assert kk_mush[0].term == "саңырауқұлақ"

def test_loan_words_marked_not_native():
    # 本地语言区的借词应标 loan;俄语区保持 russian
    for country in ("KZ", "UZ", "KG", "TJ", "TM"):
        for q in iter_country_queries(country):
            if q.language == "ru":
                assert q.term_origin == "russian"
            elif q.term in ("шампиньон", "вешенка", "шиитаке", "эноки", "эринги"):
                assert q.term_origin == "loan", f"{country}/{q.language}/{q.term} 应标为借词"

# ── ② 塔吉克俄语优先 ───────────────────────────────────────────────────

def test_tajik_russian_first():
    langs = [q.language for q in iter_country_queries("TJ")]
    # 俄语词必须先于塔语词出现(电商俄语标题为主)
    assert langs.index("ru") < langs.index("tg")

# ── ③ 哈萨克语非食品误匹配排除 ─────────────────────────────────────────

def test_kaspi_excludes_mushroom_shaped_electrode():
    # "蘑菇形电极"是 saңырауқұлақ 搜索的已知非食品误匹配
    assert KASPI_NON_FOOD.search("Саңырауқұлақ тәрізді электрод")
    assert KASPI_NON_FOOD.search("электрод")

def test_kaspi_keeps_real_mushroom():
    assert not KASPI_NON_FOOD.search("Шампиньоны свежие 500 г")
    assert not KASPI_NON_FOOD.search("Грибы вешенки 1 кг")

def test_taxonomy_excludes_electrode():
    result = classify("Саңырауқұлақ тәрізді электрод 3 шт")
    assert result["status"] == "excluded"

def test_taxonomy_keeps_real_food():
    result = classify("Саңырауқұлақ шампиньоны 500 г")
    assert result["status"] in ("classified", "ambiguous")

# ── ④ SIAT 1308 命名约定 ───────────────────────────────────────────────

def test_siat_1308_constants():
    import fetch_wholesale_index as fwi
    uz = [s for s in fwi.SOURCES if s["country"] == "UZ"][0]
    assert uz["page_id"] == "1308"
    assert uz["stat_code"] == "1.11.03.0001"
    assert "批发" not in uz["indicator"]  # 诚实命名:市场/商店平均价,非批发价
    assert "市场" in uz["indicator"]
