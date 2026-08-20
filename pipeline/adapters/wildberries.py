"""Wildberries 公开买家搜索/商品卡接口；国家必须经纬度探测验证。"""
import hashlib
import re
from urllib.parse import urlencode
from utils import safe_get

SEARCH_ENDPOINT="https://search.wb.ru/exactmatch/ru/common/v9/search"
DETAIL_ENDPOINT="https://card.wb.ru/cards/v1/detail"
GEO_ENDPOINT="https://user-geo-data.wildberries.ru/get-geo-info"
DESTINATIONS={
 "KZ":{"dest":"234","currency":"KZT","locale":"kz","latitude":43.238949,"longitude":76.889709,"city":"Almaty"},
 "UZ":{"dest":"495","currency":"UZS","locale":"uz","latitude":41.299496,"longitude":69.240073,"city":"Tashkent"},
 "KG":{"dest":"286","currency":"KGS","locale":"kg","latitude":42.874621,"longitude":74.569762,"city":"Bishkek"},
 "TJ":{"dest":"123589606","currency":"TJS","locale":"tj","latitude":38.559772,"longitude":68.787038,"city":"Dushanbe"},
 # 阿什哈巴德实测回落莫斯科 dest=-1257786/locale=ru，不得启用。
}

def discover_destination(country):
 cfg=DESTINATIONS.get(country)
 if not cfg:return None,"unsupported_country"
 response=safe_get(GEO_ENDPOINT,params={"latitude":cfg["latitude"],"longitude":cfg["longitude"],"currency":cfg["currency"]},retries=2,backoff=3)
 if not response:return None,"geo_api_unreachable"
 try:data=response.json()
 except (ValueError,AttributeError):return None,"geo_invalid_response"
 xinfo=dict(part.split("=",1) for part in str(data.get("xinfo") or "").split("&") if "=" in part)
 if data.get("locale")!=cfg["locale"] or str(data.get("currency") or "").upper()!=cfg["currency"] or xinfo.get("dest")!=cfg["dest"]:
  return None,"destination_country_mismatch"
 return {**cfg,"address":data.get("address"),"verified":True},None

class WildberriesAdapter:
 def __init__(self,config):self.config=config
 @staticmethod
 def _products(payload):
  return ((payload.get("data") or {}).get("products") or payload.get("products") or []) if isinstance(payload,dict) else []
 @staticmethod
 def _price(item):
  units=item.get("salePriceU") or item.get("priceU")
  if isinstance(units,(int,float)) and units>0:return float(units)/100
  for size in item.get("sizes") or []:
   price=(size.get("price") or {}).get("product")
   if isinstance(price,(int,float)) and price>0:return float(price)/100
  return None
 def collect_many(self):
  country=self.config["country"]
  expected=DESTINATIONS.get(country)
  if not expected:return [],"unsupported_country"
  if str(self.config.get("dest"))!=expected["dest"] or self.config.get("currency")!=expected["currency"] or not self.config.get("dest_verified"):
   return [],"destination_not_verified"
  rows={};successful_requests=0
  for query in self.config.get("queries",["шампиньоны","вешенки"]):
   params={"appType":1,"curr":expected["currency"].lower(),"dest":expected["dest"],"query":query,"resultset":"catalog","spp":30}
   response=safe_get(f"{SEARCH_ENDPOINT}?{urlencode(params)}",retries=2,backoff=3)
   if not response:continue
   try:products=self._products(response.json())
   except (ValueError,AttributeError):continue
   successful_requests+=1
   for item in products:
    product_id=str(item.get("id") or "");title=str(item.get("name") or "").strip();price=self._price(item)
    if not product_id or not title or not price:continue
    rows[product_id]={**self.config,"platform_product_id":product_id,"url":f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx","original_title":title,"current_price":price,"raw_price_text":str(price),"source_type":"json_api","delivery_dest":expected["dest"],"delivery_locale":expected["locale"],"dest_verified":True,"page_fingerprint":hashlib.sha256(response.content).hexdigest()}
  if rows:
   # 详情接口仅复核首批商品，不用空详情覆盖已验证搜索价。
   ids=list(rows)[:max(0,int(self.config.get("detail_limit",3)))]
   for product_id in ids:
    detail=safe_get(DETAIL_ENDPOINT,params={"appType":1,"curr":expected["currency"].lower(),"dest":expected["dest"],"nm":product_id},retries=1)
    if not detail:continue
    try:products=self._products(detail.json())
    except (ValueError,AttributeError):continue
    if products:
     confirmed=self._price(products[0])
     if confirmed:rows[product_id]["current_price"]=confirmed;rows[product_id]["raw_price_text"]=str(confirmed);rows[product_id]["detail_verified"]=True
   return list(rows.values()),None
  return [],"no_products" if successful_requests else "api_unreachable"
