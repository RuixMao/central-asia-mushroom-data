"""中亚五国食用菌多语检索词矩阵。

本地语言和俄语都是真实的检索任务,language 不只是入库标签。
检索结果会保留 query_language/query_term/query_species,便于评估每个词的产出。

词源标注(2026-08-18 人工核实):
  - native:本地语言原生词(如哈语 саңырауқұлақ、吉语 козу карын、塔语 занбӯруғ)
  - loan:俄语/国际借词,当地电商实际常用(如 шампьон/вешенка/шиитаке/эноки/эринги)
  - russian:俄语词

用途:
  - loan/russian 词召回率高(电商主流),native 词用于发现本地商家
  - 哈萨克语 саңырауқұлақ 是 native 总称,搜索会命中"蘑菇形电极"等非食品,
    调用方必须配合食品分类过滤(见 taxonomy NON_FOOD / Kaspi 适配器)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    country: str
    species_id: str
    language: str
    term: str
    term_origin: str = "russian"  # native / loan / russian


# 每国均含本地语言和俄语。外来菌种名保留当地平台实际使用的借词写法。
# term 为 (词, 词源),origin 标记 native/loan/russian。
COUNTRY_SEARCH_TERMS = {
    "KZ": {
        "kk": {
            "mushrooms": (("саңырауқұлақ", "native"),),
            "button_mushroom": (("шампиньон", "loan"),),
            "oyster_mushroom": (("вешенка", "loan"),),
            "shiitake": (("шиитаке", "loan"),),
            "enoki": (("эноки", "loan"),),
            "king_oyster_mushroom": (("эринги", "loan"),),
            "morel": (("сморчок", "loan"),),
            "porcini": (("ақ саңырауқұлақ", "native"),),
            "chanterelle": (("лисичка", "loan"),),
            "honey_fungus": (("опята", "loan"),),
            "suillus": (("маслята", "loan"),),
            "saffron_milk_cap": (("рыжик", "loan"),),
            "milk_mushroom": (("груздь", "loan"),),
            "blewit": (("синеножка", "loan"),),
        },
        "ru": {
            "mushrooms": (("грибы", "russian"),),
            "button_mushroom": (("шампиньоны", "russian"),),
            "oyster_mushroom": (("вешенки", "russian"),),
            "shiitake": (("шиитаке", "russian"),),
            "enoki": (("эноки", "russian"),),
            "king_oyster_mushroom": (("эринги", "russian"),),
            "morel": (("сморчки", "russian"),),
            "porcini": (("белые грибы", "russian"),),
            "chanterelle": (("лисички", "russian"),),
            "honey_fungus": (("опята", "russian"),),
            "suillus": (("маслята", "russian"),),
            "saffron_milk_cap": (("рыжики", "russian"),),
            "milk_mushroom": (("грузди", "russian"),),
            "blewit": (("синеножки", "russian"),),
        },
    },
    "UZ": {
        "uz": {
            "mushrooms": (("qo'ziqorin", "native"), ("qo‘ziqorin", "native")),
            "button_mushroom": (("shampinyon", "loan"), ("sampinyon", "loan")),
            "oyster_mushroom": (("veshenka", "loan"),),
            "shiitake": (("shiitake", "loan"),),
            "enoki": (("enoki", "loan"),),
            "king_oyster_mushroom": (("eringi", "loan"),),
            "morel": (("smorchok", "loan"),),
            "porcini": (("oq qo'ziqorin", "native"),),
            "chanterelle": (("lisichka", "loan"),),
            "honey_fungus": (("opyata", "loan"),),
            "suillus": (("maslyata", "loan"),),
            "saffron_milk_cap": (("rijik", "loan"),),
            "milk_mushroom": (("gruzd", "loan"),),
            "blewit": (("sinenojka", "loan"),),
        },
        "ru": {
            "mushrooms": (("грибы", "russian"),),
            "button_mushroom": (("шампиньоны", "russian"),),
            "oyster_mushroom": (("вешенки", "russian"),),
            "shiitake": (("шиитаке", "russian"),),
            "enoki": (("эноки", "russian"),),
            "king_oyster_mushroom": (("эринги", "russian"),),
            "morel": (("сморчки", "russian"),),
            "porcini": (("белые грибы", "russian"),),
            "chanterelle": (("лисички", "russian"),),
            "honey_fungus": (("опята", "russian"),),
            "suillus": (("маслята", "russian"),),
            "saffron_milk_cap": (("рыжики", "russian"),),
            "milk_mushroom": (("грузди", "russian"),),
            "blewit": (("синеножки", "russian"),),
        },
    },
    "KG": {
        "ky": {
            "mushrooms": (("козу карын", "native"),),
            "button_mushroom": (("шампиньондор", "loan"),),
            "oyster_mushroom": (("вешенка", "loan"),),
            "shiitake": (("шиитаке", "loan"),),
            "enoki": (("эноки", "loan"),),
            "king_oyster_mushroom": (("эринги", "loan"),),
            "morel": (("сморчок", "loan"),),
            "porcini": (("ак козу карын", "native"),),
            "chanterelle": (("лисичка", "loan"),),
            "honey_fungus": (("опята", "loan"),),
            "suillus": (("маслята", "loan"),),
            "saffron_milk_cap": (("рыжик", "loan"),),
            "milk_mushroom": (("груздь", "loan"),),
            "blewit": (("синеножка", "loan"),),
        },
        "ru": {
            "mushrooms": (("грибы", "russian"),),
            "button_mushroom": (("шампиньоны", "russian"),),
            "oyster_mushroom": (("вешенки", "russian"),),
            "shiitake": (("шиитаке", "russian"),),
            "enoki": (("эноки", "russian"),),
            "king_oyster_mushroom": (("эринги", "russian"),),
            "morel": (("сморчки", "russian"),),
            "porcini": (("белые грибы", "russian"),),
            "chanterelle": (("лисички", "russian"),),
            "honey_fungus": (("опята", "russian"),),
            "suillus": (("маслята", "russian"),),
            "saffron_milk_cap": (("рыжики", "russian"),),
            "milk_mushroom": (("грузди", "russian"),),
            "blewit": (("синеножки", "russian"),),
        },
    },
    "TJ": {
        # 塔吉克电商以俄语标题为主:俄语词优先、塔语词补充
        "ru": {
            "mushrooms": (("грибы", "russian"),),
            "button_mushroom": (("шампиньоны", "russian"),),
            "oyster_mushroom": (("вешенки", "russian"),),
            "shiitake": (("шиитаке", "russian"),),
            "enoki": (("эноки", "russian"),),
            "king_oyster_mushroom": (("эринги", "russian"),),
            "morel": (("сморчки", "russian"),),
            "porcini": (("белые грибы", "russian"),),
            "chanterelle": (("лисички", "russian"),),
            "honey_fungus": (("опята", "russian"),),
            "suillus": (("маслята", "russian"),),
            "saffron_milk_cap": (("рыжики", "russian"),),
            "milk_mushroom": (("грузди", "russian"),),
            "blewit": (("синеножки", "russian"),),
        },
        "tg": {
            "mushrooms": (("занбӯруғ", "native"),),
            "button_mushroom": (("шампиньон", "loan"),),
            "oyster_mushroom": (("вешенка", "loan"),),
            "shiitake": (("шиитаке", "loan"),),
            "enoki": (("эноки", "loan"),),
            "king_oyster_mushroom": (("эринги", "loan"),),
            "morel": (("занбӯруғи сморчок", "native"),),
            "porcini": (("занбӯруғи сафед", "native"),),
            "chanterelle": (("занбӯруғи лисичка", "native"),),
            "honey_fungus": (("занбӯруғи асал", "native"),),
            "suillus": (("занбӯруғи маслята", "native"),),
            "saffron_milk_cap": (("занбӯруғи рыжик", "native"),),
            "milk_mushroom": (("занбӯруғи груздь", "native"),),
            "blewit": (("занбӯруғи синеножка", "native"),),
        },
    },
    "TM": {
        "tk": {
            "mushrooms": (("kömelek", "native"), ("komelek", "native")),
            "button_mushroom": (("gelin kömelek", "native"), ("şampinýon", "loan")),
            "oyster_mushroom": (("weşenka kömelegi", "native"),),
            "shiitake": (("şiitake", "loan"),),
            "enoki": (("enoki", "loan"),),
            "king_oyster_mushroom": (("eringi", "loan"),),
            "morel": (("smorçok", "loan"),),
            "porcini": (("ak kömelek", "native"),),
            "chanterelle": (("lisçka", "loan"),),
            "honey_fungus": (("opyata", "loan"),),
            "suillus": (("maslata", "loan"),),
            "saffron_milk_cap": (("rıjik", "loan"),),
            "milk_mushroom": (("gruzd", "loan"),),
            "blewit": (("sinenojka", "loan"),),
        },
        "ru": {
            "mushrooms": (("грибы", "russian"),),
            "button_mushroom": (("шампиньоны", "russian"),),
            "oyster_mushroom": (("вешенки", "russian"),),
            "shiitake": (("шиитаке", "russian"),),
            "enoki": (("эноки", "russian"),),
            "king_oyster_mushroom": (("эринги", "russian"),),
            "morel": (("сморчки", "russian"),),
            "porcini": (("белые грибы", "russian"),),
            "chanterelle": (("лисички", "russian"),),
            "honey_fungus": (("опята", "russian"),),
            "suillus": (("маслята", "russian"),),
            "saffron_milk_cap": (("рыжики", "russian"),),
            "milk_mushroom": (("грузди", "russian"),),
            "blewit": (("синеножки", "russian"),),
        },
    },
}


def iter_country_queries(country, species_ids=None, include_variants=False):
    """生成稳定、去重的检索任务。

    默认每个语言/菌种只取一个主词；只有平台证明需要拼写变体时才开启全部变体。
    语言顺序按 COUNTRY_SEARCH_TERMS 定义(塔吉克:俄语在前,塔语在后)。
    """
    wanted = set(species_ids or ())
    seen = set()
    for language, species in COUNTRY_SEARCH_TERMS[country].items():
        for species_id, terms in species.items():
            if wanted and species_id not in wanted:
                continue
            selected = terms if include_variants else terms[:1]
            for term, origin in selected:
                key = (language, term.casefold())
                if key in seen:
                    continue
                seen.add(key)
                yield SearchQuery(country, species_id, language, term, term_origin=origin)
