"""Publish today's verified Thailand mushroom listings for the daily report."""
import datetime as dt
import hashlib
from zoneinfo import ZoneInfo

from utils import log, post_to_site, safe_get

DATE = dt.datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
BIGC = "https://www.bigc.co.th/group/hyp-mushroom"
MAKRO = "https://www.makro.pro/th/c/collections/Yummy%20and%20Healthy%20Mushrooms"
# platform id, name, title, species, grams, THB price, URL, regular price
ROWS = [
 ("bigc-th","Big C Online","วี อาร์ เฟร็ช เห็ดเข็มทอง 500 ก.","enoki",500,30,BIGC,None),
 ("bigc-th","Big C Online","เห็ดเข็มทอง 200 ก.","enoki",200,9,BIGC,18),
 ("bigc-th","Big C Online","วี อาร์ เฟร็ช เห็ดหิมะขาว 100 ก.","snow_fungus",100,17,BIGC,None),
 ("bigc-th","Big C Online","เห็ดแชมปิญอง 150 ก.","button_mushroom",150,65,BIGC,None),
 ("bigc-th","Big C Online","วีอาร์เฟรช เห็ดหูหนูดำ แพ็ค 200 ก.","wood_ear",200,39,BIGC,None),
 ("bigc-th","Big C Online","วี อาร์ เฟร็ช เห็ดแชมปิญองน้ำตาล 150 ก.","button_mushroom",150,89,BIGC,None),
 ("bigc-th","Big C Online","วีอาร์เฟรช เห็ดหอมสด 100 ก.","shiitake",100,35,BIGC,None),
 ("makro-pro-th","Makro PRO","เอโร่ เห็ดเข็มทอง 1 กก.","enoki",1000,57,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดนางรมหลวง ขนาด L 1 กก.","king_oyster_mushroom",1000,65,MAKRO,None),
 ("makro-pro-th","Makro PRO","สหฟาร์มเห็ด เห็ดเข็มทอง 200 ก.","enoki",200,15,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดเข็มทอง 500 ก.","enoki",500,29,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดหอมสด เบอร์ใหญ่ 300 ก.","shiitake",300,69,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดนางรมหลวง 500 ก.","king_oyster_mushroom",500,49,MAKRO,None),
 ("makro-pro-th","Makro PRO","เอโร่ เห็ดหอมกลาง 500 ก.","shiitake",500,220,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดแชมปิญองน้ําตาลเล็ก 200 ก.","button_mushroom",200,75,MAKRO,None),
 ("makro-pro-th","Makro PRO","เห็ดหูหนู 200 ก.","wood_ear",200,27,MAKRO,None),
]

def run():
 rate = float(safe_get("https://fxapi.app/api/usd.json", retries=2).json()["rates"]["THB"])
 now = dt.datetime.now(dt.timezone.utc).isoformat()
 for pid, pname, title, species, grams, price, url, regular in ROWS:
  key = hashlib.sha1(f"{pid}|{title}".encode()).hexdigest()[:16]
  usdkg = round(price / (grams / 1000) / rate, 2)
  post_to_site("/api/ingest/snapshot", {"metric":"price_retail","country":"TH","source":pid,"data":{
   "product_key":f"{pid}:{key}","species_id":species,"original_title":title,"product_form":"fresh",
   "product_shape":"whole","processing_state":"fresh","packaging_type":"packaged","package_display":f"{grams:g} g","package_source":"page_title",
   "platform_name":pname,"status":"live","validation_status":"valid","price_local":price,
   "regular_price_local":regular,"currency":"THB","price_usd":round(price/rate,2),
   "normalized_price_usd_per_kg":usdkg,"observed_at":DATE,"retrieved_at":now,"source_url":url}})
 log(f"today Thailand retail rows written: {len(ROWS)}")

if __name__ == "__main__": run()
