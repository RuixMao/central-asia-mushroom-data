import hashlib,re
from bs4 import BeautifulSoup
from utils import safe_get, find_price_match, response_text

PRICE=re.compile(r"(\d[\d\s]*(?:[.,]\d+)?)\s*(?:сомони|сом(?:/кг)?|[cс]\b)",re.I)
class ProductAdapter:
 def __init__(self,config):self.config=config
 def parse(self,response):
  soup=BeautifulSoup(response_text(response),"html.parser");text=" ".join(soup.get_text(" ",strip=True).split());marker=self.config.get("marker")
  if marker:
   pos=text.lower().find(marker.lower())
   if pos<0:return None,"product_marker_missing"
   text=text[pos:pos+600]
  match,price=find_price_match(soup,PRICE)
  if not match:return None,"price_missing"
  if not price:return None,"price_missing"
  return {**self.config,"original_title":self.config["title"],"current_price":price,"raw_price_text":match.group(0)},None
 def collect(self):
  response=safe_get(self.config["url"],retries=1)
  if not response:return None,"unreachable"
  parsed=self.parse(response)
  if isinstance(parsed,tuple):row,error=parsed
  else:row,error=parsed,None
  if error:return None,error
  return {**row,"page_fingerprint":hashlib.sha256(response.content).hexdigest()},None
 def collect_many(self):
  """多商品采集：默认实现为单条。渲染型适配器可覆写返回多条。"""
  row,error=self.collect()
  if error:return [],error
  return [row],None
