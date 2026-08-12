import datetime as dt
import os
from adapters.globus import GlobusAdapter
from adapters.omarket import OMarketAdapter
from adapters.zudbiyor import ZudbiyorAdapter
from adapters.magnit import MagnitAdapter
from adapters.olx import OlxAdapter
from adapters.somon import SomonAdapter
from adapters.kaspi import KaspiAdapter
from adapters.yandex import YandexMarketAdapter
from adapters.gipertm import GiperAdapter
from adapters.asmanexpress import AsmanAdapter
from taxonomy import classify,normalize_price,parse_package
from utils import log,post_to_site,safe_get,today_str

SOURCES=[
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"9905ed980f9d469888dadc3efc68b6fe000200010000","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/good/9905ed980f9d469888dadc3efc68b6fe000200010000","title":"Грибы Шампиньоны фасованные вес 1 кг","package":"1 kg","currency":"KGS","language":"ru"}),
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"fresh-oyster-category","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/catalog/grocery/category/f65c13b6fb5ffb8c5752ff03be5a71bd/a0e91ee087e645b98fb1698163a1c64f000200010000","title":"Грибы Вешенки фасованные вес 1 кг","marker":"Вешен","package":"1 kg","currency":"KGS","language":"ru"}),
(OMarketAdapter,{"platform":"omarket","platform_name":"O!Market","platform_product_id":"4450008b-61fc-4fb7-839f-c4bdd5669c5c","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://market.o.kg/ru/bishkek/produkty-pitanija/ovoschi-frukty/product/4450008b-61fc-4fb7-839f-c4bdd5669c5c/griby-shampinony-1kg","title":"Грибы Шампиньоны 300 г","package":"300 g","currency":"KGS","language":"ru"}),
(ZudbiyorAdapter,{"platform":"zudbiyor","platform_name":"Zudbiyor","platform_product_id":"141","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://zudbiyor.tj/product/141","title":"Шампиньоны целые 1 кг","package":"1 kg","currency":"TJS","language":"ru"}),
(MagnitAdapter,{"platform":"magnit-tj","platform_name":"Magnit.tj","platform_product_id":"18786","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://magnit.tj/product/show/18786","title":"Шампиньоны цена за 250 г","package":"250 g","currency":"TJS","language":"ru"}),
(OlxAdapter,{"platform":"olx-uz","platform_name":"OLX.uz","platform_product_id":"shampinony-yaschikah-ID488Lu","country":"UZ","city":"Tashkent","collection_point_id":"TASHKENT_POINT_01","url":"https://www.olx.uz/d/obyavlenie/shampinony-v-yaschikah-otbornye-svezhie-rossiya-ID488Lu.html","title":"Шампиньоны в ящиках отборные свежие","package":"1 box","currency":"UZS","language":"ru"}),
(SomonAdapter,{"platform":"somon","platform_name":"Somon.tj","platform_product_id":"15687107","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://somon.tj/adv/15687107_griby-shampinon/","title":"Грибы шампиньоны","package":"1 kg","currency":"TJS","language":"ru"}),
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
]
def rates():
 r=safe_get("https://fxapi.app/api/usd.json",retries=2);return r.json()["rates"],r.json().get("timestamp")
def run():
 fx,fx_time=rates();items=[];errors=[];wanted_platform=os.getenv("PLATFORM","").strip();wanted_point=os.getenv("COLLECTION_POINT","").strip();dry_run=os.getenv("DRY_RUN","false").lower()=="true"
 for Adapter,config in SOURCES:
  if wanted_platform and config["platform"]!=wanted_platform:continue
  if wanted_point and config["collection_point_id"]!=wanted_point:continue
  rows,error=Adapter(config).collect_many()
  if error:errors.append({"platform":config["platform"],"reason":error});continue
  for row in rows:
   # 商品规格优先从标题解析（多商品搜索页各商品规格不同），否则用配置默认值
   package_text=row.get("package") or ""
   pkg_from_title=parse_package(row.get("original_title") or "")
   if pkg_from_title["parse_status"]=="valid" and pkg_from_title["quantity_kg"]:
    package_text=row["original_title"]
   category=classify(row["original_title"]);norm=normalize_price(row["current_price"],package_text);local_per_usd=float(fx[row["currency"]]);now=dt.datetime.now(dt.timezone.utc).isoformat()
   items.append({**row,"product_url":row.pop("url"),"original_language":row.pop("language"),"species_id":category["species_id"],"product_form":category["product_form"],"classification_status":category["status"],"classification_confidence":category["confidence"],"classification_evidence":category["evidence"],"observed_at":now,"observation_date":today_str(),"package_value":norm["value"],"package_unit":norm["unit"],"normalized_quantity_kg":norm["quantity_kg"],"normalized_price_per_kg":norm["price_per_kg"],"price_usd":round(row["current_price"]/local_per_usd,2),"usd_rate_local_per_usd":local_per_usd,"fx_source":"fxapi.app","fx_timestamp":fx_time,"in_stock":True,"source_type":row.pop("source_type","server_html"),"validation_status":"valid" if category["confidence"]>=.9 and norm["price_per_kg"] else "needs_review"})
 if items and not dry_run:post_to_site("/api/ingest/prices",{"items":items})
 # 写 price_retail 快照（AI 日报与网页端价格表的数据源）。
 # 注意：快照接口的 data.observed_at 必须是 YYYY-MM-DD（日报按 ==today 过滤），
 # 不能用 items 里的 ISO 时间戳；成功写 live、失败源写 gap，确保缺口可见。
 if not dry_run:
  today=today_str()
  for it in items:
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":it["country"],"source":it["platform"],"data":{"variety":it.get("species_id") or it["original_title"][:40],"status":"live","price_local":it["current_price"],"price_usd":it["price_usd"],"currency":it["currency"],"observed_at":today}})
  for e in errors:
   country=next((c["country"] for _,c in SOURCES if c["platform"]==e["platform"]),"")
   post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":e["platform"],"data":{"status":"gap","reason":e["reason"],"observed_at":today}})
 log(f"平台适配器完成：有效 {len(items)} 条，失败 {len(errors)} 条，dry_run={dry_run}；{errors}")
 if not items:raise RuntimeError("没有有效价格")
if __name__=="__main__":run()
