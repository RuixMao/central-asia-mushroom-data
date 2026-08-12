import hashlib,re
from bs4 import BeautifulSoup
from utils import safe_get

PRICE=re.compile(r"(\d[\d\s]*(?:[.,]\d+)?)\s*(?:сомони|сом(?:/кг)?|с\b)",re.I)
class ProductAdapter:
 def __init__(self,config):self.config=config
 def collect(self):
  response=safe_get(self.config["url"],retries=1)
  if not response:return None,"unreachable"
  text=" ".join(BeautifulSoup(response.text,"html.parser").get_text(" ",strip=True).split());marker=self.config.get("marker")
  if marker:
   pos=text.lower().find(marker.lower())
   if pos<0:return None,"product_marker_missing"
   text=text[pos:pos+600]
  match=PRICE.search(text)
  if not match:return None,"price_missing"
  price=float(match.group(1).replace(" ","").replace(",","."))
  if price<=0:return None,"zero_price"
  return {**self.config,"original_title":self.config["title"],"current_price":price,"raw_price_text":match.group(0),"page_fingerprint":hashlib.sha256(response.content).hexdigest()},None
