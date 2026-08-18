"""中亚五国食用菌多语检索词矩阵。

本地语言和俄语都是真实的检索任务，language 不只是入库标签。
检索结果会保留 query_language/query_term/query_species，便于评估每个词的产出。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    country: str
    species_id: str
    language: str
    term: str


# 每国均含本地语言和俄语。外来菌种名保留当地平台实际使用的借词写法。
COUNTRY_SEARCH_TERMS = {
    "KZ": {
        "kk": {
            "mushrooms": ("саңырауқұлақ",),
            "button_mushroom": ("шампиньон",),
            "oyster_mushroom": ("вешенка",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
        "ru": {
            "mushrooms": ("грибы",),
            "button_mushroom": ("шампиньоны",),
            "oyster_mushroom": ("вешенки",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
    },
    "UZ": {
        "uz": {
            "mushrooms": ("qo'ziqorin", "qo‘ziqorin"),
            "button_mushroom": ("shampinyon", "sampinyon"),
            "oyster_mushroom": ("veshenka",),
            "shiitake": ("shiitake",),
            "enoki": ("enoki",),
            "king_oyster_mushroom": ("eringi",),
        },
        "ru": {
            "mushrooms": ("грибы",),
            "button_mushroom": ("шампиньоны",),
            "oyster_mushroom": ("вешенки",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
    },
    "KG": {
        "ky": {
            "mushrooms": ("козу карын",),
            "button_mushroom": ("шампиньондор",),
            "oyster_mushroom": ("вешенка",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
        "ru": {
            "mushrooms": ("грибы",),
            "button_mushroom": ("шампиньоны",),
            "oyster_mushroom": ("вешенки",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
    },
    "TJ": {
        "tg": {
            "mushrooms": ("занбӯруғ",),
            "button_mushroom": ("шампиньон",),
            "oyster_mushroom": ("вешенка",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
        "ru": {
            "mushrooms": ("грибы",),
            "button_mushroom": ("шампиньоны",),
            "oyster_mushroom": ("вешенки",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
    },
    "TM": {
        "tk": {
            "mushrooms": ("kömelek", "komelek"),
            "button_mushroom": ("gelin kömelek", "şampinýon"),
            "oyster_mushroom": ("weşenka kömelegi",),
            "shiitake": ("şiitake",),
            "enoki": ("enoki",),
            "king_oyster_mushroom": ("eringi",),
        },
        "ru": {
            "mushrooms": ("грибы",),
            "button_mushroom": ("шампиньоны",),
            "oyster_mushroom": ("вешенки",),
            "shiitake": ("шиитаке",),
            "enoki": ("эноки",),
            "king_oyster_mushroom": ("эринги",),
        },
    },
}


def iter_country_queries(country, species_ids=None, include_variants=False):
    """生成稳定、去重的检索任务。

    默认每个语言/菌种只取一个主词；只有平台证明需要拼写变体时才开启全部变体。
    """
    wanted = set(species_ids or ())
    seen = set()
    for language, species in COUNTRY_SEARCH_TERMS[country].items():
        for species_id, terms in species.items():
            if wanted and species_id not in wanted:
                continue
            selected = terms if include_variants else terms[:1]
            for term in selected:
                key = (language, term.casefold())
                if key in seen:
                    continue
                seen.add(key)
                yield SearchQuery(country, species_id, language, term)
