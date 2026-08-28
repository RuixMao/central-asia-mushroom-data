import datetime as dt
import json
import os
from collections import Counter
from pathlib import Path
from urllib.parse import quote
from review import review_record
from sanity import apply_sanity_validation, review_sanity_outliers
from auto_review import resolve_pending_reviews
from investigate_review import investigate_pending_reviews
from product_dimensions import describe_product
from adapters.globus import GlobusAdapter
from adapters.omarket import OMarketAdapter
from adapters.zudbiyor import ZudbiyorAdapter
from adapters.magnit import MagnitAdapter
from adapters.olx import OlxSearchAdapter
from adapters.lochin import LochinAdapter
from adapters.makro import MakroAdapter
from adapters.yukber import YukberAdapter
from adapters.somon import SomonAdapter
from adapters.kaspi import KaspiAdapter
from adapters.yandex import YandexMarketAdapter
from adapters.gipertm import GiperAdapter
from adapters.asmanexpress import AsmanAdapter
from adapters.arbuz import ArbuzAdapter
from adapters.catalog_search import CatalogSearchAdapter
from adapters.wildberries import DESTINATIONS as WB_DESTINATIONS,WildberriesAdapter
from adapters.flagma import FlagmaAdapter
from adapters.uzum import UzumAdapter
from adapters.magnum import MagnumAdapter
from config import TARGET_SPECIES
from search_queries import SearchQuery,iter_country_queries
from taxonomy import classify,normalize_price,parse_package
from utils import log,post_to_data,post_to_site,safe_get,today_str

VOLUME_KG_PER_L=float(os.getenv("MUSHROOM_VOLUME_KG_PER_L", "1.0"))

SOURCES=[
(ArbuzAdapter,{"platform":"arbuz-kz","platform_name":"Arbuz.kz","platform_product_id":"fresh-mushroom-catalog","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","url":"https://arbuz.kz/ru/almaty/catalog/cat/225444-griby","title":"Свежие грибы","package":"","currency":"KZT","language":"ru"}),
(ArbuzAdapter,{"platform":"arbuz-kz","platform_name":"Arbuz.kz","platform_product_id":"frozen-mushroom-catalog","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","url":"https://arbuz.kz/ru/almaty/catalog/cat/225587-griby_zamorozhennye","title":"Замороженные грибы","package":"","currency":"KZT","language":"ru"}),
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"9905ed980f9d469888dadc3efc68b6fe000200010000","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/good/9905ed980f9d469888dadc3efc68b6fe000200010000","title":"Грибы Шампиньоны фасованные вес 1 кг","package":"1 kg","currency":"KGS","language":"ru"}),
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"fresh-oyster-category","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/catalog/grocery/category/f65c13b6fb5ffb8c5752ff03be5a71bd/a0e91ee087e645b98fb1698163a1c64f000200010000","title":"Грибы Вешенки фасованные вес 1 кг","marker":"Вешен","package":"1 kg","currency":"KGS","language":"ru"}),
(OMarketAdapter,{"platform":"omarket","platform_name":"O!Market","platform_product_id":"4450008b-61fc-4fb7-839f-c4bdd5669c5c","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://market.o.kg/ru/bishkek/produkty-pitanija/ovoschi-frukty/product/4450008b-61fc-4fb7-839f-c4bdd5669c5c/griby-shampinony-1kg","title":"Грибы Шампиньоны 300 г","package":"300 g","currency":"KGS","language":"ru"}),
(CatalogSearchAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"catalog-search","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/search?q=грибы","title":"Каталог грибов","package":"","currency":"KGS","language":"ru"}),
(CatalogSearchAdapter,{"platform":"omarket","platform_name":"O!Market","platform_product_id":"catalog-search","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://market.o.kg/bishkek/search?q=грибы","title":"Каталог грибов","package":"","currency":"KGS","language":"ru"}),
(CatalogSearchAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"local-mushroom-category","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ky-kg/catalog/grocery/category/774448e3d08d450aadf655a818663d39/2708e9cc8a2043679251e7592ee059ff000200010000","title":"Козу карын","package":"","currency":"KGS","language":"ky","query_language":"ky","query_term":"козу карын","query_species":"mushrooms"}),
(ZudbiyorAdapter,{"platform":"zudbiyor","platform_name":"Zudbiyor","platform_product_id":"141","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://zudbiyor.tj/product/141","title":"Шампиньоны целые 1 кг","package":"1 kg","currency":"TJS","language":"ru"}),
(MagnitAdapter,{"platform":"magnit-tj","platform_name":"Magnit.tj","platform_product_id":"18786","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://magnit.tj/product/show/18786","title":"Шампиньоны цена за 250 г","package":"250 g","currency":"TJS","language":"ru"}),
(OlxSearchAdapter,{"platform":"olx-uz","platform_name":"OLX.uz поиск","platform_product_id":"search-fresh-mushrooms","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://www.olx.uz/list/q-грибы-свежие/","title":"Свежие грибы","package":"","currency":"UZS","language":"ru"}),
(LochinAdapter,{"platform":"lochin-uz","platform_name":"Lochin","platform_product_id":"7057","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://lochin.uz/product/7057","title":"Грибы шампиньоны, вес","marker":"Грибы шампиньоны, вес","package":"","currency":"UZS","language":"ru"}),
(LochinAdapter,{"platform":"lochin-uz","platform_name":"Lochin","platform_product_id":"7508","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://lochin.uz/product/7508","title":"Грибы Вешенки, вес","marker":"Грибы Вешенки, вес","package":"","currency":"UZS","language":"ru"}),
(LochinAdapter,{"platform":"lochin-uz","platform_name":"Lochin","platform_product_id":"712","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://lochin.uz/product/712","title":"Грибы Шампиньоны Сказка 1л","marker":"Грибы Шампиньоны Сказка 1л","package":"1 l","currency":"UZS","language":"ru"}),
(YukberAdapter,{"platform":"yukber-uz","platform_name":"Yukber","platform_product_id":"YK1820","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://yukber.uz/uz/sabzovotlar/YK1820_uz","title":"Qo'ziqorin Shampinyon 1kg","package":"1 kg","currency":"UZS","language":"uz"}),
(YukberAdapter,{"platform":"yukber-uz","platform_name":"Yukber","platform_product_id":"YK0143","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://yukber.uz/uz/YK0143_uz","title":"Qo'ziqorin veshenski 1l","package":"1 l","currency":"UZS","language":"uz"}),
(MakroAdapter,{"platform":"makro-uz","platform_name":"Makro","platform_product_id":"catalog-scan","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://makromarket.uz/catalog","title":"Makro mushroom catalog","package":"","currency":"UZS","language":"uz"}),
(SomonAdapter,{"platform":"somon","platform_name":"Somon.tj","platform_product_id":"15687107","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://somon.tj/adv/15687107_griby-shampinon/","title":"Грибы шампиньоны","package":"","currency":"TJS","language":"ru"}),
(KaspiAdapter,{"platform":"kaspi-kz","platform_name":"Kaspi Магазин","platform_product_id":"search-shampinon","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","url":"https://kaspi.kz/shop/search/?text=шампиньон","title":"Шампиньоны свежие 500 г","package":"500 g","currency":"KZT","language":"ru"}),
(YandexMarketAdapter,{"platform":"yandex-uz","platform_name":"Yandex Market UZ","platform_product_id":"search-shampinon","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://market.yandex.uz/search?text=шампиньоны","title":"Шампиньоны свежие","package":"1 kg","currency":"UZS","language":"ru"}),
(GiperAdapter,{"platform":"gipertm","platform_name":"Giper.tm","platform_product_id":"200763","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://gipertm.com/catalog/product/200763","title":"Gelinkömelek (şampinýon) Tokaýçy 300 gr","package":"300 g","currency":"TMT","language":"tk"}),
# Uzum(乌兹别克最大电商):渲染型,本地验证码拦截,CI 代理下可达
(UzumAdapter,{"platform":"uzum-uz","platform_name":"Uzum","platform_product_id":"search-mushrooms-ru","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://uzum.uz/ru/search?query=грибы","title":"Грибы","package":"","currency":"UZS","language":"ru","query_language":"ru","query_term":"грибы","query_species":"mushrooms"}),
(UzumAdapter,{"platform":"uzum-uz","platform_name":"Uzum","platform_product_id":"search-mushrooms-uz","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://uzum.uz/uz/search?query=qo%27ziqorin","title":"Qo'ziqorin","package":"","currency":"UZS","language":"uz","query_language":"uz","query_term":"qo'ziqorin","query_species":"mushrooms"}),
# Magnum(哈萨克连锁商超):Nuxt SPA,商品异步加载,渲染框架待 CI 逆向 API
(MagnumAdapter,{"platform":"magnum-kz","platform_name":"Magnum","platform_product_id":"catalog-mushrooms","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","url":"https://magnum.kz/catalog?city=almaty","title":"Грибы","package":"","currency":"KZT","language":"ru","query_language":"ru","query_term":"грибы","query_species":"mushrooms"}),
(GiperAdapter,{"platform":"gipertm","platform_name":"Giper.tm","platform_product_id":"201768","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://gipertm.com/catalog/product/201768","title":"Gelinkömelek (şampinýon) Tokaýçy 800 gr","package":"800 g","currency":"TMT","language":"tk"}),
(GiperAdapter,{"platform":"gipertm","platform_name":"Giper.tm","platform_product_id":"207977","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://gipertm.com/catalog/product/207977","title":"Esmo marinadlanan şampinýon kömelekleri 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(GiperAdapter,{"platform":"gipertm","platform_name":"Giper.tm","platform_product_id":"205866","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://gipertm.com/catalog/product/205866","title":"Şampinon kömelekleri Ra-Ra kesilen 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(GiperAdapter,{"platform":"gipertm","platform_name":"Giper.tm","platform_product_id":"3917","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://gipertm.com/catalog/product/3917","title":"RITA Bütewi Şampion kömelekler 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(AsmanAdapter,{"platform":"asmanexpress","platform_name":"Asman Express","platform_product_id":"44506","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://asmanexpress.com/mini/product/44506","title":"Eyran komelek 1000 gr","package":"1000 g","currency":"TMT","language":"tk"}),
(AsmanAdapter,{"platform":"asmanexpress","platform_name":"Asman Express","platform_product_id":"48014","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://asmanexpress.com/mini/product/48014","title":"Красная Линия kesilen kömelekler 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(AsmanAdapter,{"platform":"asmanexpress","platform_name":"Asman Express","platform_product_id":"944","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://asmanexpress.com/mini/product/944","title":"Eklin Gelin kömelek bütin 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(AsmanAdapter,{"platform":"asmanexpress","platform_name":"Asman Express","platform_product_id":"1308","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://asmanexpress.com/mini/product/1308","title":"Rita bitin Gelin kömelekli 400 gr","package":"400 g","currency":"TMT","language":"tk"}),
(AsmanAdapter,{"platform":"asmanexpress","platform_name":"Asman Express","platform_product_id":"12389","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://asmanexpress.com/mini/product/12389","title":"Rita Kesilen şampinýonlar 200 gr","package":"200 g","currency":"TMT","language":"tk"}),
(FlagmaAdapter,{"platform":"flagma-kz","platform_name":"Flagma.kz","platform_product_id":"catalog-search","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","url":"https://flagma.kz/ru/products/q=грибы/","title":"B2B грибы","package":"","currency":"KZT","language":"ru"}),
(FlagmaAdapter,{"platform":"flagma-uz","platform_name":"Flagma.uz","platform_product_id":"catalog-search","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://flagma.uz/ru/products/q=грибы/","title":"B2B грибы","package":"","currency":"UZS","language":"ru"}),
(FlagmaAdapter,{"platform":"flagma-kg","platform_name":"Flagma.kg","platform_product_id":"catalog-search","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://flagma-kg.com/ru/products/q=грибы/","title":"B2B грибы","package":"","currency":"KGS","language":"ru"}),
(FlagmaAdapter,{"platform":"flagma-tj","platform_name":"Flagma.tj","platform_product_id":"catalog-search","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://flagma-tj.com/ru/products/q=грибы/","title":"B2B грибы","package":"","currency":"TJS","language":"ru"}),
(FlagmaAdapter,{"platform":"flagma-tm","platform_name":"Flagma-TM","platform_product_id":"catalog-search","country":"TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","url":"https://flagma-tm.com/ru/products/q=грибы/","title":"B2B грибы","package":"","currency":"TMT","language":"ru"}),
(CatalogSearchAdapter,{"platform":"champa-garden-la","platform_name":"Champa Garden Shop","platform_product_id":"fresh-shiitake-100g","country":"LA","city":"Vientiane","collection_point_id":"VIENTIANE_POINT_01","url":"https://champagardenshop.com/products/fresh-shitake-100g-pack-barcode-50103200","title":"ເຫັດຫອມສົດ 100g Fresh Shitake 100g pack","package":"100 g","currency":"LAK","language":"lo"}),
(CatalogSearchAdapter,{"platform":"bach-hoa-xanh-vn","platform_name":"Bách hoá XANH","platform_product_id":"fresh-mushroom-category","country":"VN","city":"Ho Chi Minh City","collection_point_id":"HCMC_POINT_01","url":"https://www.bachhoaxanh.com/nam-tuoi/","title":"Nấm các loại","package":"","currency":"VND","language":"vi"}),
(CatalogSearchAdapter,{"platform":"bigc-th","platform_name":"Big C Online","platform_product_id":"mushroom-category","country":"TH","city":"Bangkok","collection_point_id":"BANGKOK_POINT_01","url":"https://www.bigc.co.th/category/mushroom","title":"เห็ด","package":"","currency":"THB","language":"th"}),
(CatalogSearchAdapter,{"platform":"foodpanda-mm","platform_name":"Capital Hypermarket / foodpanda","platform_product_id":"capital-hypermarket-mushrooms","country":"MM","city":"Yangon","collection_point_id":"YANGON_POINT_01","url":"https://www.foodpanda.com.mm/en/shop/z2su/capital-hypermarket-h001-dawbon-z2su","title":"Mushrooms","package":"","currency":"MMK","language":"en"}),
(CatalogSearchAdapter,{"platform":"lucky-foodpanda-kh","platform_name":"Lucky Supermarket / foodpanda","platform_product_id":"lucky-olympia-mushrooms","country":"KH","city":"Phnom Penh","collection_point_id":"PHNOM_PENH_POINT_01","url":"https://www.foodpanda.com.kh/en/shop/bq32/lucky-supermarket-olympia","title":"Fresh mushrooms","package":"","currency":"USD","language":"en"}),
]

# 中亚任务使用本地语言和俄语，东南亚任务使用本地语言和英语。对可靠的商品搜索站扫描全品类；
# 对容易限流或仅有通用搜索页的站点，只用食用菌总词发现商品，再由 taxonomy 分类。
SOURCES=[entry for entry in SOURCES if entry[1].get("platform_product_id") not in {"search-shampinon", "catalog-search"}]

def _search_config(base, task, url):
 return {**base,"platform_product_id":f"search-{task.species_id}-{task.language}",
         "url":url,"title":task.term,"language":task.language,
         "query_language":task.language,"query_term":task.term,"query_species":task.species_id}

# daily: 双语总词搜索页一次返回多商品；expanded: 周期性扫描再逐菌种搜索。
search_species=("mushrooms",*TARGET_SPECIES) if os.getenv("SEARCH_QUERY_MODE", "daily").lower()=="expanded" else ("mushrooms",)

for task in iter_country_queries("KZ", search_species):
 SOURCES.append((KaspiAdapter,_search_config(
  {"platform":"kaspi-kz","platform_name":"Kaspi Магазин","country":"KZ","city":"Almaty","collection_point_id":"ALMATY_POINT_01","package":"","currency":"KZT"},
  task,f"https://kaspi.kz/shop/search/?text={quote(task.term)}")))

for task in iter_country_queries("UZ", search_species):
 SOURCES.append((YandexMarketAdapter,_search_config(
  {"platform":"yandex-uz","platform_name":"Yandex Market UZ","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","package":"","currency":"UZS"},
  task,f"https://market.yandex.uz/search?text={quote(task.term)}")))

catalog_searches=(
 ("KG",CatalogSearchAdapter,{"platform":"globus","platform_name":"Globus Online","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","currency":"KGS"},"https://globus-online.kg/{locale}/search?q={query}"),
 ("KG",CatalogSearchAdapter,{"platform":"omarket","platform_name":"O!Market","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","currency":"KGS"},"https://market.o.kg/bishkek/search?q={query}"),
 ("TJ",CatalogSearchAdapter,{"platform":"somon","platform_name":"Somon.tj","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","currency":"TJS"},"https://somon.tj/search/?q={query}"),
 ("KZ",FlagmaAdapter,{"platform":"flagma-kz","platform_name":"Flagma.kz","city":"Almaty","collection_point_id":"ALMATY_POINT_01","currency":"KZT"},"https://flagma.kz/ru/products/q={query}/"),
 ("UZ",FlagmaAdapter,{"platform":"flagma-uz","platform_name":"Flagma.uz","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","currency":"UZS"},"https://flagma.uz/ru/products/q={query}/"),
 ("KG",FlagmaAdapter,{"platform":"flagma-kg","platform_name":"Flagma.kg","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","currency":"KGS"},"https://flagma-kg.com/ru/products/q={query}/"),
 ("TJ",FlagmaAdapter,{"platform":"flagma-tj","platform_name":"Flagma.tj","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","currency":"TJS"},"https://flagma-tj.com/ru/products/q={query}/"),
 ("TM",FlagmaAdapter,{"platform":"flagma-tm","platform_name":"Flagma-TM","city":"Ashgabat","collection_point_id":"ASHGABAT_POINT_01","currency":"TMT"},"https://flagma-tm.com/ru/products/q={query}/"),
)
for country,adapter,base,url_template in catalog_searches:
 # somon 总词(грибы)实测返回教材/种子(被 NON_FOOD 过滤),具体菌种词才能命中真商品;
 # 其余平台跑双语总词(日常模式)即可。
 species_scope = TARGET_SPECIES if adapter is CatalogSearchAdapter and base.get("platform") == "somon" else ("mushrooms",)
 tasks=([SearchQuery(country,"mushrooms","ru",term,"russian") for term in ("грибы","шампиньоны","вешенки","мицелий")] if adapter is FlagmaAdapter else iter_country_queries(country,species_scope))
 for task in tasks:
  # Flagma 各站只索引俄语(本地语言词实测返回 404),只跑俄语任务;
  # 其余平台跑双语(本地语言 + 俄语)
  if adapter is FlagmaAdapter and task.language != "ru":
   continue
  locale="ky-kg" if task.language=="ky" else "ru-kg"
  url=url_template.format(locale=locale,query=quote(task.term))
  SOURCES.append((adapter,_search_config({**base,"country":country,"package":""},task,url)))

# Wildberries 的配送区 dest 必须按国家实测，避免把默认俄罗斯结果错归入中亚。
# CI 可用 WB_DESTS_JSON 显式启用，例如 {"KZ":"已核验的dest"}。
try:
 wb_dests=json.loads(os.getenv("WB_DESTS_JSON", "{}")) or {code:meta["dest"] for code,meta in WB_DESTINATIONS.items()}
except json.JSONDecodeError:
 wb_dests={}
wb_meta={"KZ":("KZT","Almaty","ALMATY_POINT_01"),"UZ":("UZS","Tashkent","TASHKENT_POINT_01"),"KG":("KGS","Bishkek","BISHKEK_POINT_01"),"TJ":("TJS","Dushanbe","DUSHANBE_POINT_01"),"TM":("TMT","Ashgabat","ASHGABAT_POINT_01")}
for code,dest in wb_dests.items():
 if code not in wb_meta:continue
 currency,city,point=wb_meta[code]
 queries=["шампиньоны","вешенки","шиитаке","эноки"]
 verified=code in WB_DESTINATIONS and str(dest)==WB_DESTINATIONS[code]["dest"]
 SOURCES.append((WildberriesAdapter,{"platform":f"wildberries-{code.lower()}","platform_name":"Wildberries","platform_product_id":"catalog-search","country":code,"city":city,"collection_point_id":point,"url":"https://search.wb.ru/","title":"Каталог грибов","package":"","currency":currency,"language":"ru","queries":queries,"query_languages":["ru"],"dest":str(dest),"dest_verified":verified,"detail_limit":3}))

def rates():
 r=safe_get("https://fxapi.app/api/usd.json",retries=2);return r.json()["rates"],r.json().get("timestamp")

# ── 渲染/静态分离 ────────────────────────────────────────────────────────
# 渲染型平台(CatalogSearchAdapter 子类等需要真实浏览器)耗时是静态源的 5-10 倍。
# COLLECTION_MODE 控制日常主链路不跑渲染任务(时间可控),渲染源走独立低频 workflow:
#   static(默认):只跑静态源,日常 5 分钟内完成
#   rendered:    只跑渲染源(独立 workflow 用)
#   all:         全部(手动补采用)
RENDERED_PLATFORMS = {"kaspi-kz", "yandex-uz", "uzum-uz"}
# 长期无产出的平台(面议 B2B / 无蘑菇数据),日常模式跳过避免空跑,
# 仅在 expanded/all 模式或显式指定 PLATFORM 时采集(降频不删除)。
LOW_FREQUENCY_PLATFORMS = {
 "flagma-kz", "flagma-uz", "flagma-kg", "flagma-tj", "flagma-tm", "makro-uz",
 # 2026-08-24 五国线上复测：搜索接口持续 429，详情页持续 403/498，
 # 且逐商品重试会把单国日常任务拖长数分钟。保留适配器和国家配送区，
 # 但只在显式 PLATFORM=wildberries-xx 或 COLLECTION_MODE=all 时低频复测。
 "wildberries-kz", "wildberries-uz", "wildberries-kg", "wildberries-tj", "wildberries-tm",
}
COLLECTION_MODE = os.getenv("COLLECTION_MODE", "static").strip().lower()

def run():
 fx,fx_time=rates();items=[];errors=[];active_configs=[];seen_products=set();query_runs=[];excluded_by_query=Counter();wanted_country=os.getenv("COUNTRY","").strip().upper();wanted_platform=os.getenv("PLATFORM","").strip();wanted_point=os.getenv("COLLECTION_POINT","").strip();dry_run=os.getenv("DRY_RUN","false").lower()=="true";query_task_limit=max(0,int(os.getenv("QUERY_TASK_LIMIT","0") or 0));executed_query_tasks=0
 for Adapter,config in SOURCES:
  if wanted_country and config["country"]!=wanted_country:continue
  if wanted_platform and config["platform"]!=wanted_platform:continue
  if wanted_point and config["collection_point_id"]!=wanted_point:continue
  is_rendered=config["platform"] in RENDERED_PLATFORMS
  if COLLECTION_MODE=="static" and is_rendered:continue
  if COLLECTION_MODE=="rendered" and not is_rendered:continue
  # 低频平台:日常(static)跳过,显式指定 platform 或 all/rendered 才跑
  if config["platform"] in LOW_FREQUENCY_PLATFORMS and COLLECTION_MODE=="static" and not wanted_platform:
   continue
  if config.get("query_term") and query_task_limit and executed_query_tasks>=query_task_limit:
   continue
  if config.get("query_term"):
   executed_query_tasks+=1
  active_configs.append(config)
  rows,error=Adapter(config).collect_many()
  if config.get("query_term"):
   query_runs.append({"platform":config["platform"],"language":config["query_language"],"term":config["query_term"],"species":config["query_species"],"candidate_count":len(rows),"status":"gap" if error else "live","reason":error})
  if error:errors.append({"platform":config["platform"],"reason":error});continue
  for row in rows:
   product_key=(row["country"],row["platform"],row["collection_point_id"],row["platform_product_id"])
   if product_key in seen_products:continue
   seen_products.add(product_key)
   # 商品规格优先从标题解析（多商品搜索页各商品规格不同），否则用配置默认值
   package_text=row.get("package") or ""
   pkg_from_title=parse_package(row.get("original_title") or "",allow_volume=True,volume_kg_per_l=VOLUME_KG_PER_L)
   if pkg_from_title["parse_status"] in ("valid","valid_volume_estimate") and pkg_from_title["quantity_kg"]:
    package_text=row["original_title"]
    package_source="page_title_volume_estimate" if pkg_from_title["parse_status"]=="valid_volume_estimate" else "page_title"
   elif row.get("package_verified") is True and parse_package(package_text,allow_volume=True,volume_kg_per_l=VOLUME_KG_PER_L)["parse_status"] in ("valid","valid_volume_estimate"):
    package_source="page_structured_volume_estimate" if parse_package(package_text,allow_volume=True,volume_kg_per_l=VOLUME_KG_PER_L)["parse_status"]=="valid_volume_estimate" else "page_structured_data"
   else:
    package_text="";package_source="unverified"
   category=classify(row["original_title"],description=row.get("description") or "",category=row.get("category") or "",language=row.get("language") or "")
   if category["status"]=="excluded" and row.get("b2b_category")=="cultivation_input":
    category={"species_id":None,"product_form":"cultivation_input","status":"review_required","confidence":.99,"evidence":[{"field":"title","rule":"cultivation_input"}]}
   elif category["status"]=="excluded":
    excluded_by_query[(row["platform"],row.get("query_language") or "fixed_page",row.get("query_term") or "",row.get("query_species") or "")]+=1
    continue
   norm=normalize_price(row["current_price"],package_text,allow_volume=True,volume_kg_per_l=VOLUME_KG_PER_L);local_per_usd=float(fx[row["currency"]]);now=dt.datetime.now(dt.timezone.utc).isoformat()
   dimensions=describe_product(row["original_title"],category["product_form"],norm["value"],norm["unit"],row)
   item={**row,**dimensions,"product_url":row.pop("url"),"original_language":row.pop("language"),"species_id":category["species_id"],"product_form":category["product_form"],"classification_status":category["status"],"classification_confidence":category["confidence"],"classification_evidence":category["evidence"],"observed_at":now,"observation_date":today_str(),"package_value":norm["value"],"package_unit":norm["unit"],"package_source":package_source,"package_conversion_basis":norm.get("conversion_basis"),"normalized_quantity_kg":norm["quantity_kg"],"normalized_price_per_kg":norm["price_per_kg"],"price_usd":round(row["current_price"]/local_per_usd,2),"usd_rate_local_per_usd":local_per_usd,"fx_source":"fxapi.app","fx_timestamp":fx_time,"in_stock":row.get("in_stock"),"source_type":row.pop("source_type","server_html")}
   review=review_record(item)
   normalized_usd_per_kg=round(norm["price_per_kg"]/local_per_usd,2) if norm.get("price_per_kg") is not None else None
   sanity_review=apply_sanity_validation(review,category["species_id"],row["country"],normalized_usd_per_kg)
   items.append({**item,**sanity_review,"normalized_price_usd_per_kg":normalized_usd_per_kg})
 investigation_stats=investigate_pending_reviews(items)
 auto_reviewed=review_sanity_outliers(items)
 # 自动复核闭环：可解释异常自动放行，证据不足项自动隔离；后续定时采集
 # 会再次读取源页面，解析器一旦获得完整证据即可自然恢复为 valid。
 quarantine_unresolved=os.getenv("AUTO_REVIEW_QUARANTINE", "1").lower() not in {"0","false","no"}
 review_stats=resolve_pending_reviews(items,quarantine_unresolved=quarantine_unresolved)
 if items and not dry_run:
  payload={"items":items}
  post_to_site("/api/ingest/prices",payload)
  # yinheng.site is the canonical production database. A legacy mirror must
  # never turn an otherwise successful collection into a failed daily run.
  try:
   post_to_data("/api/ingest/prices",payload)
  except RuntimeError as exc:
   log(f"legacy data mirror warning: {exc}")
 # 写 price_retail 快照（AI 日报与网页端价格表的数据源）。
 # 注意：快照接口的 data.observed_at 必须是 YYYY-MM-DD（日报按 ==today 过滤），
 # 不能用 items 里的 ISO 时间戳；成功写 live、失败源写 gap，确保缺口可见。
 if not dry_run:
  today=today_str()
  for it in items:
   if it["validation_status"]=="rejected":continue
   labels=TARGET_SPECIES.get(it["species_id"],{})
   normalized_usd_per_kg=it.get("normalized_price_usd_per_kg")
   package_display=f'{it["package_value"]:g} {it["package_unit"]}' if it.get("package_value") and it.get("package_unit") else ""
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":it["country"],"source":it["platform"],"data":{"product_key":f'{it["platform"]}:{it["collection_point_id"]}:{it["platform_product_id"]}',"species_id":it["species_id"],"species_zh":labels.get("zh",it["species_id"]),"species_foreign":labels.get("ru") or labels.get("en"),"original_title":it["original_title"],"original_language":it["original_language"],"discovery":{"query_language":it.get("query_language"),"query_term":it.get("query_term"),"query_species":it.get("query_species")},"product_form":it["product_form"],"product_shape":it["product_shape"],"processing_state":it["processing_state"],"packaging_type":it["packaging_type"],"brand":it.get("brand"),"origin_country":it.get("origin_country"),"package_display":package_display,"package_source":it["package_source"],"package_conversion_basis":it.get("package_conversion_basis"),"platform_id":it["platform"],"platform_name":it["platform_name"],"status":"live","validation_status":it["validation_status"],"auto_review_status":it.get("auto_review_status"),"auto_review_reason":it.get("auto_review_reason"),"sanity_outlier":it["sanity_outlier"],"sanity_reason":it["sanity_reason"],"price_local":it["current_price"],"price_usd":it["price_usd"],"normalized_price_usd_per_kg":normalized_usd_per_kg,"currency":it["currency"],"observed_at":today,"retrieved_at":it["observed_at"],"source_url":it["product_url"]}})
  successful_platforms={it["platform"] for it in items}
  platform_errors={e["platform"]:e["reason"] for e in errors if e["platform"] not in successful_platforms}
  for platform,reason in platform_errors.items():
   country=next((c["country"] for _,c in SOURCES if c["platform"]==platform),"")
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":platform,"data":{"status":"gap","reason":reason,"observed_at":today}})
  for query in query_runs:
   country=next((c["country"] for c in active_configs if c["platform"]==query["platform"]),"")
   try:
    post_to_site("/api/ingest/snapshot",{"metric":"search_query_health","country":country,"source":query["platform"],"data":{**query,"observed_at":today}})
   except RuntimeError as exc:
    # health 数据是辅助诊断型,API 拒绝时降级为日志,不阻塞主采集
    log(f"search_query_health 写入失败(降级): {exc}")
  platform_configs={c["platform"]:c for c in active_configs}
  for platform,config in platform_configs.items():
   count=sum(1 for it in items if it["platform"]==platform)
   valid_count=sum(1 for it in items if it["platform"]==platform and it["validation_status"]=="valid")
   pending_count=sum(1 for it in items if it["platform"]==platform and it["validation_status"]=="needs_review")
   quarantined_count=sum(1 for it in items if it["platform"]==platform and it["validation_status"]=="rejected")
   health_status="live" if valid_count else ("needs_review" if pending_count else ("quarantined" if quarantined_count else "gap"))
   platform_queries=[q for q in query_runs if q["platform"]==platform]
   try:
    post_to_site("/api/ingest/snapshot",{"metric":"source_health","country":config["country"],"source":platform,"data":{"status":health_status,"candidate_count":count,"valid_count":valid_count,"needs_review_count":pending_count,"quarantined_count":quarantined_count,"reason":platform_errors.get(platform),"search_coverage":{"languages":sorted({q["language"] for q in platform_queries}),"query_count":len(platform_queries),"successful_query_count":sum(q["status"]=="live" for q in platform_queries)},"observed_at":today}})
   except RuntimeError as exc:
    log(f"source_health 写入失败(降级): {exc}")
 valid_items=[it for it in items if it["validation_status"]=="valid"]
 summary={"candidates":len(items),"valid":len(valid_items),"needs_review":sum(it["validation_status"]=="needs_review" for it in items),"quarantined":sum(it["validation_status"]=="rejected" for it in items),"investigation":investigation_stats,"auto_review":review_stats,
          "valid_by_country":dict(sorted(Counter(it["country"] for it in valid_items).items())),
          "valid_by_platform":dict(sorted(Counter(it["platform"] for it in valid_items).items())),
          "valid_by_species":dict(sorted(Counter(it["species_id"] for it in valid_items).items())),
          "discovered_by_query_language":dict(sorted(Counter(it.get("query_language") or "fixed_page" for it in valid_items).items()))}
 audit_output=os.getenv("AUDIT_OUTPUT","").strip()
 if audit_output:
  audit_rows=[]
  for query in query_runs:
   matched=[it for it in items if it["platform"]==query["platform"] and it.get("query_language")==query["language"] and it.get("query_term")==query["term"] and it.get("query_species")==query["species"]]
   key=(query["platform"],query["language"],query["term"],query["species"])
   actual=Counter(it["species_id"] or "unclassified" for it in matched)
   audit_rows.append({**query,"retained_count":len(matched),"valid_count":sum(it["validation_status"]=="valid" for it in matched),"needs_review_count":sum(it["validation_status"]!="valid" for it in matched),"excluded_count":excluded_by_query[key],"classified_species":dict(sorted(actual.items())),"off_target_count":sum(it.get("species_id") not in (query["species"],None) for it in matched) if query["species"]!="mushrooms" else 0})
  audit_items=[{"country":it["country"],"platform":it["platform"],"title":it["original_title"],"species_id":it["species_id"],"product_shape":it["product_shape"],"processing_state":it["processing_state"],"packaging_type":it["packaging_type"],"brand":it.get("brand"),"origin_country":it.get("origin_country"),"classification_status":it["classification_status"],"validation_status":it["validation_status"],"review_decision":it["review_decision"],"review_reasons":it["review_reasons"],"review_actions":it["review_actions"],"price_local":it["current_price"],"currency":it["currency"],"package_value":it["package_value"],"package_unit":it["package_unit"],"query_language":it.get("query_language"),"query_term":it.get("query_term"),"product_url":it["product_url"]} for it in items]
  audit={"generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),"dry_run":dry_run,"country_filter":wanted_country or None,"collection_mode":COLLECTION_MODE,"search_query_mode":os.getenv("SEARCH_QUERY_MODE","daily"),"summary":summary,"items":audit_items,"queries":audit_rows,"errors":errors}
  output_path=Path(audit_output)
  output_path.parent.mkdir(parents=True,exist_ok=True)
  output_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
  log(f"检索词审计报告已写入: {output_path}")
 sanity_count=sum(1 for it in items if it.get("sanity_outlier"));sanity_pct=(sanity_count/len(items)*100) if items else 0
 log(f"sanity: {sanity_count} 条超出区间（{sanity_pct:.1f}%），已标记 needs_review")
 log(f"sanity review: {auto_reviewed} 条已找到有页面规格证据的价格差异原因")
 log(f"targeted investigation: {json.dumps(investigation_stats,ensure_ascii=False)}")
 log(f"auto review loop: {json.dumps(review_stats,ensure_ascii=False)}")
 log(f"平台适配器完成：{json.dumps(summary,ensure_ascii=False)}，失败任务 {len(errors)} 条，dry_run={dry_run}；{errors}")
 if not items and not dry_run:raise RuntimeError("没有有效价格")
if __name__=="__main__":run()
