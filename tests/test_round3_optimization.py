import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/"pipeline"))

from taxonomy import classify
from adapters.catalog_search import _parse_price
from adapters.flagma import MUSHROOM as FLAGMA_MUSHROOM, NON_FOOD as FLAGMA_NON_FOOD
from adapters.catalog_search import MUSHROOM as CATALOG_MUSHROOM, NON_FOOD as CATALOG_NON_FOOD

def test_flagma_mycelium_excluded():
    # 菌丝/培养包不得被 flagma 当作蘑菇商品(修复:从 MUSHROOM 移到 NON_FOOD)
    assert FLAGMA_MUSHROOM.search("Мицелий вешенки оптом")
    assert FLAGMA_NON_FOOD.search("Мицелий вешенки оптом")
    assert FLAGMA_NON_FOOD.search("Грибной блок вешенки")
    assert FLAGMA_NON_FOOD.search("Субстрат для выращивания грибов")

def test_flagma_real_product_still_matches():
    assert FLAGMA_MUSHROOM.search("Грибы шампиньоны оптом")
    assert not FLAGMA_NON_FOOD.search("Грибы шампиньоны оптом")

def test_catalog_textbook_excluded():
    # 教材/种子/科普(搜索"грибы"时常出现)不得作为食品报价
    assert CATALOG_MUSHROOM.search("Биология 5 класс: бактерии грибы растения")
    assert CATALOG_NON_FOOD.search("Биология 5 класс: бактерии грибы растения")
    assert CATALOG_NON_FOOD.search("Семена грибов шампиньонов")

def test_catalog_real_product_kept():
    assert CATALOG_MUSHROOM.search("Грибы шампиньоны 1 кг")
    assert not CATALOG_NON_FOOD.search("Грибы шампиньоны 1 кг")

def test_parse_price_thousands():
    assert _parse_price("45 000") == 45000
    assert _parse_price("45,000") == 45000
    assert _parse_price("1,234.56") == 1234.56
    assert _parse_price("128,70") == 128.70
    assert _parse_price("12.5") == 12.5
    assert _parse_price("abc") is None

def test_classify_local_generic_ambiguous():
    # 本地语言总称 -> ambiguous(蘑菇但品种待核),不强行归类
    for title in ("Саңырауқұлақ 500 г", "Занбӯруғ 300 г", "Козу карын 1 кг"):
        result = classify(title)
        assert result["status"] == "ambiguous"
        assert result["species_id"] is None

def test_classify_honey_fungus_local():
    # 蜜环菌本地语言词(塔吉克语/哈萨克语)可识别
    assert classify("Занбӯруғи асал 1 кг")["species_id"] == "honey_fungus"
    assert classify("Бал саңырауқұлағы 500 г")["species_id"] == "honey_fungus"
