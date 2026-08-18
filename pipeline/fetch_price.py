import datetime as dt
import json
import os
from collections import Counter
from urllib.parse import quote
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
from adapters.wildberries import WildberriesAdapter
from adapters.flagma import FlagmaAdapter
from config import TARGET_SPECIES
from search_queries import iter_country_queries
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
]

# 五国检索任务均同时包含本地语言和俄语。对可靠的商品搜索站扫描全品类；
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
 for task in iter_country_queries(country, species_scope):
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
 wb_dests=json.loads(os.getenv("WB_DESTS_JSON", "{}"))
except json.JSONDecodeError:
 wb_dests={}
wb_meta={"KZ":("KZT","Almaty","ALMATY_POINT_01"),"UZ":("UZS","Tashkent","TASHKENT_POINT_01"),"KG":("KGS","Bishkek","BISHKEK_POINT_01"),"TJ":("TJS","Dushanbe","DUSHANBE_POINT_01"),"TM":("TMT","Ashgabat","ASHGABAT_POINT_01")}
for code,dest in wb_dests.items():
 if code not in wb_meta:continue
 currency,city,point=wb_meta[code]
 queries=list(iter_country_queries(code,TARGET_SPECIES))
 SOURCES.append((WildberriesAdapter,{"platform":f"wildberries-{code.lower()}","platform_name":"Wildberries","platform_product_id":"catalog-search","country":code,"city":city,"collection_point_id":point,"url":"https://search.wb.ru/","title":"Каталог грибов","package":"","currency":currency,"language":"multi","queries":[q.term for q in queries],"query_languages":sorted({q.language for q in queries}),"dest":str(dest)}))

def rates():
 r=safe_get("https://fxapi.app/api/usd.json",retries=2);return r.json()["rates"],r.json().get("timestamp")
def run():
 fx,fx_time=rates();items=[];errors=[];active_configs=[];seen_products=set();query_runs=[];wanted_platform=os.getenv("PLATFORM","").strip();wanted_point=os.getenv("COLLECTION_POINT","").strip();dry_run=os.getenv("DRY_RUN","false").lower()=="true"
 for Adapter,config in SOURCES:
  if wanted_platform and config["platform"]!=wanted_platform:continue
  if wanted_point and config["collection_point_id"]!=wanted_point:continue
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
   if category["status"]=="excluded":continue
   norm=normalize_price(row["current_price"],package_text,allow_volume=True,volume_kg_per_l=VOLUME_KG_PER_L);local_per_usd=float(fx[row["currency"]]);now=dt.datetime.now(dt.timezone.utc).isoformat()
   is_valid=category["status"]=="classified" and category["confidence"]>=.9 and norm["price_per_kg"] is not None and package_source!="unverified"
   items.append({**row,"product_url":row.pop("url"),"original_language":row.pop("language"),"species_id":category["species_id"],"product_form":category["product_form"],"classification_status":category["status"],"classification_confidence":category["confidence"],"classification_evidence":category["evidence"],"observed_at":now,"observation_date":today_str(),"package_value":norm["value"],"package_unit":norm["unit"],"package_source":package_source,"package_conversion_basis":norm.get("conversion_basis"),"normalized_quantity_kg":norm["quantity_kg"],"normalized_price_per_kg":norm["price_per_kg"],"price_usd":round(row["current_price"]/local_per_usd,2),"usd_rate_local_per_usd":local_per_usd,"fx_source":"fxapi.app","fx_timestamp":fx_time,"in_stock":row.get("in_stock"),"source_type":row.pop("source_type","server_html"),"validation_status":"valid" if is_valid else "needs_review"})
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
   if it["validation_status"]!="valid":continue
   labels=TARGET_SPECIES.get(it["species_id"],{})
   normalized_usd_per_kg=round(it["normalized_price_per_kg"]/it["usd_rate_local_per_usd"],2)
   package_display=f'{it["package_value"]:g} {it["package_unit"]}' if it.get("package_value") and it.get("package_unit") else ""
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":it["country"],"source":it["platform"],"data":{"product_key":f'{it["platform"]}:{it["collection_point_id"]}:{it["platform_product_id"]}',"species_id":it["species_id"],"species_zh":labels.get("zh",it["species_id"]),"species_foreign":labels.get("ru") or labels.get("en"),"original_title":it["original_title"],"original_language":it["original_language"],"discovery":{"query_language":it.get("query_language"),"query_term":it.get("query_term"),"query_species":it.get("query_species")},"product_form":it["product_form"],"package_display":package_display,"package_source":it["package_source"],"package_conversion_basis":it.get("package_conversion_basis"),"platform_id":it["platform"],"platform_name":it["platform_name"],"status":"live","price_local":it["current_price"],"price_usd":it["price_usd"],"normalized_price_usd_per_kg":normalized_usd_per_kg,"currency":it["currency"],"observed_at":today,"retrieved_at":it["observed_at"],"source_url":it["product_url"]}})
  successful_platforms={it["platform"] for it in items}
  platform_errors={e["platform"]:e["reason"] for e in errors if e["platform"] not in successful_platforms}
  for platform,reason in platform_errors.items():
   country=next((c["country"] for _,c in SOURCES if c["platform"]==platform),"")
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":platform,"data":{"status":"gap","reason":reason,"observed_at":today}})
  for query in query_runs:
   country=next((c["country"] for _,c in active_configs if c["platform"]==query["platform"]),"")
   post_to_site("/api/ingest/snapshot",{"metric":"search_query_health","country":country,"source":query["platform"],"data":{**query,"observed_at":today}})
  platform_configs={c["platform"]:c for c in active_configs}
  for platform,config in platform_configs.items():
   count=sum(1 for it in items if it["platform"]==platform)
   valid_count=sum(1 for it in items if it["platform"]==platform and it["validation_status"]=="valid")
   health_status="live" if valid_count else ("needs_review" if count else "gap")
   platform_queries=[q for q in query_runs if q["platform"]==platform]
   post_to_site("/api/ingest/snapshot",{"metric":"source_health","country":config["country"],"source":platform,"data":{"status":health_status,"candidate_count":count,"valid_count":valid_count,"needs_review_count":count-valid_count,"reason":platform_errors.get(platform),"search_coverage":{"languages":sorted({q["language"] for q in platform_queries}),"query_count":len(platform_queries),"successful_query_count":sum(q["status"]=="live" for q in platform_queries)},"observed_at":today}})
 valid_items=[it for it in items if it["validation_status"]=="valid"]
 summary={"candidates":len(items),"valid":len(valid_items),"needs_review":len(items)-len(valid_items),
          "valid_by_country":dict(sorted(Counter(it["country"] for it in valid_items).items())),
          "valid_by_platform":dict(sorted(Counter(it["platform"] for it in valid_items).items())),
          "valid_by_species":dict(sorted(Counter(it["species_id"] for it in valid_items).items())),
          "discovered_by_query_language":dict(sorted(Counter(it.get("query_language") or "fixed_page" for it in valid_items).items()))}
 log(f"平台适配器完成：{json.dumps(summary,ensure_ascii=False)}，失败任务 {len(errors)} 条，dry_run={dry_run}；{errors}")
 if not items and not dry_run:raise RuntimeError("没有有效价格")
if __name__=="__main__":run()
