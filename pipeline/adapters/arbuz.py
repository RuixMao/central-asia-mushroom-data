import hashlib
import html
import json
import re
from urllib.parse import urljoin

from .base import ProductAdapter
from utils import safe_get

class ArbuzAdapter(ProductAdapter):
 def parse(self,response):
  data=response.json() if "json" in response.headers.get("content-type","") else json.loads(response.text)
  product=data.get("product",data)
  return {**self.config,"original_title":product["name"],"current_price":float(product["price"]),"regular_price":product.get("old_price"),"in_stock":product.get("available",True),"raw_price_text":str(product["price"])}

 def collect_many(self):
  response=safe_get(self.config["url"],retries=2,backoff=3)
  if not response:return [],"unreachable"
  rows={}
  for encoded in re.findall(r':product="([^"]+)"',response.text):
   try:product=json.loads(html.unescape(encoded))
   except (ValueError,TypeError):continue
   product_id=str(product.get("id") or "")
   title=str(product.get("name") or "").strip()
   price=product.get("priceSpecial") or product.get("priceActual")
   if not product_id or not title or not isinstance(price,(int,float)) or price<=0:continue
   if not product.get("isAvailable",True):continue
   uri=str(product.get("uri") or "")
   rows[product_id]={**self.config,"platform_product_id":product_id,
    "url":urljoin(response.url,uri),"original_title":title,"current_price":float(price),
    "package":"1 kg" if product.get("isWeighted") and product.get("measure") in ("кг","kg") else title,
    "regular_price":product.get("pricePrevious") or None,"in_stock":True,
    "raw_price_text":str(price),"source_type":"embedded_catalog_json",
    "page_fingerprint":hashlib.sha256(response.content).hexdigest()}
  return (list(rows.values()),None) if rows else ([],"no_mushroom_products")
