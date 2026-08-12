import datetime as dt
import os
from adapters.globus import GlobusAdapter
from adapters.omarket import OMarketAdapter
from adapters.zudbiyor import ZudbiyorAdapter
from adapters.magnit import MagnitAdapter
from taxonomy import classify,normalize_price
from utils import log,post_to_site,safe_get,today_str

SOURCES=[
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"9905ed980f9d469888dadc3efc68b6fe000200010000","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/good/9905ed980f9d469888dadc3efc68b6fe000200010000","title":"Грибы Шампиньоны фасованные вес 1 кг","package":"1 kg","currency":"KGS","language":"ru"}),
(GlobusAdapter,{"platform":"globus","platform_name":"Globus Online","platform_product_id":"fresh-oyster-category","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://globus-online.kg/ru-kg/catalog/grocery/category/f65c13b6fb5ffb8c5752ff03be5a71bd/a0e91ee087e645b98fb1698163a1c64f000200010000","title":"Грибы Вешенки фасованные вес 1 кг","marker":"Вешен","package":"1 kg","currency":"KGS","language":"ru"}),
(OMarketAdapter,{"platform":"omarket","platform_name":"O!Market","platform_product_id":"4450008b-61fc-4fb7-839f-c4bdd5669c5c","country":"KG","city":"Bishkek","collection_point_id":"BISHKEK_POINT_01","url":"https://market.o.kg/ru/bishkek/produkty-pitanija/ovoschi-frukty/product/4450008b-61fc-4fb7-839f-c4bdd5669c5c/griby-shampinony-1kg","title":"Грибы Шампиньоны 300 г","package":"300 g","currency":"KGS","language":"ru"}),
(ZudbiyorAdapter,{"platform":"zudbiyor","platform_name":"Zudbiyor","platform_product_id":"141","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://zudbiyor.tj/product/141","title":"Шампиньоны целые 1 кг","package":"1 kg","currency":"TJS","language":"ru"}),
(MagnitAdapter,{"platform":"magnit-tj","platform_name":"Magnit.tj","platform_product_id":"18786","country":"TJ","city":"Dushanbe","collection_point_id":"DUSHANBE_POINT_01","url":"https://magnit.tj/product/show/18786","title":"Шампиньоны цена за 250 г","package":"250 g","currency":"TJS","language":"ru"}),
]
def rates():
 r=safe_get("https://fxapi.app/api/usd.json",retries=2);return r.json()["rates"],r.json().get("timestamp")
def run():
 fx,fx_time=rates();items=[];errors=[];wanted_platform=os.getenv("PLATFORM","").strip();wanted_point=os.getenv("COLLECTION_POINT","").strip();dry_run=os.getenv("DRY_RUN","false").lower()=="true"
 for Adapter,config in SOURCES:
  if wanted_platform and config["platform"]!=wanted_platform:continue
  if wanted_point and config["collection_point_id"]!=wanted_point:continue
  row,error=Adapter(config).collect()
  if error:errors.append({"platform":config["platform"],"reason":error});continue
  category=classify(row["original_title"]);norm=normalize_price(row["current_price"],row["package"]);local_per_usd=float(fx[row["currency"]]);now=dt.datetime.now(dt.timezone.utc).isoformat()
  items.append({**row,"product_url":row.pop("url"),"original_language":row.pop("language"),"species_id":category["species_id"],"product_form":category["product_form"],"classification_status":category["status"],"classification_confidence":category["confidence"],"classification_evidence":category["evidence"],"observed_at":now,"observation_date":today_str(),"package_value":norm["value"],"package_unit":norm["unit"],"normalized_quantity_kg":norm["quantity_kg"],"normalized_price_per_kg":norm["price_per_kg"],"price_usd":round(row["current_price"]/local_per_usd,2),"usd_rate_local_per_usd":local_per_usd,"fx_source":"fxapi.app","fx_timestamp":fx_time,"in_stock":True,"source_type":"server_html","validation_status":"valid" if category["confidence"]>=.9 and norm["price_per_kg"] else "needs_review"})
 if items and not dry_run:post_to_site("/api/ingest/prices",{"items":items})
 log(f"平台适配器完成：有效 {len(items)} 条，失败 {len(errors)} 条，dry_run={dry_run}；{errors}")
 if not items:raise RuntimeError("没有有效价格")
if __name__=="__main__":run()
