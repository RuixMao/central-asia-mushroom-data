import re
from bs4 import BeautifulSoup
from .render import RenderedProductAdapter
PRICE=re.compile(r"(\d[\d\s]{2,12})\s*₸")
class KaspiAdapter(RenderedProductAdapter):
 def parse_rendered(self,html,body=""):
  soup=BeautifulSoup(html,"html.parser")
  for card in soup.select(".item-card,.product-card,[data-product-id]"):
   text=" ".join(card.get_text(" ",strip=True).split())
   if not re.search(r"шампиньон|вешенк|гриб",text,re.I):continue
   match=PRICE.search(text)
   if not match:continue
   price=float(match.group(1).replace(" ",""))
   if price<=0:continue
   link=card.find("a",href=True);url=link["href"] if link else self.config["url"]
   if url.startswith("/"):url="https://kaspi.kz"+url
   return {**self.config,"url":url,"original_title":text[:240],"current_price":price,"raw_price_text":match.group(0)},None
  return None,"price_missing"
