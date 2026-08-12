import hashlib,re
from bs4 import BeautifulSoup
from utils import safe_get

PRICE=re.compile(r"(\d[\d\s]*(?:[.,]\d+)?)\s*(?:сомони|сом(?:/кг)?|[cс]\b)",re.I)
class ProductAdapter:
 def __init__(self,config):self.config=config
 def parse(self,response):
  text=" ".join(BeautifulSoup(response.text,"html.parser").get_text(" ",strip=True).split());marker=self.config.get("marker")
  if marker:
   pos=text.lower().find(marker.lower())
   if pos<0:return None,"product_marker_missing"
   text=text[pos:pos+600]
  matches=list(PRICE.finditer(text))
  if not matches:return None,"price_missing"
  match=next((item for item in matches if float(item.group(1).replace(" ","").replace(",","."))>0),None)
  if not match:return None,"zero_price"
  price=float(match.group(1).replace(" ","").replace(",","."))
  return {**self.config,"original_title":self.config["title"],"current_price":price,"raw_price_text":match.group(0)},None
 def collect(self):
  response=safe_get(self.config["url"],retries=1)
  if not response:return None,"unreachable"
  parsed=self.parse(response)
  if isinstance(parsed,tuple):row,error=parsed
  else:row,error=parsed,None
  if error:return None,error
  return {**row,"page_fingerprint":hashlib.sha256(response.content).hexdigest()},None
