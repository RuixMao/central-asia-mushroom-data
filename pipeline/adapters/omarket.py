import re
from bs4 import BeautifulSoup
from .base import ProductAdapter
from utils import parse_price_text,response_text

META_PRICE=re.compile(r"(?:^|·)\s*(\d+(?:[.,]\d+)?)\s*(?:сом|[cс])\b",re.I)

class OMarketAdapter(ProductAdapter):
 def parse(self,response):
  soup=BeautifulSoup(response_text(response),"html.parser")
  og=soup.find("meta",property="og:title")
  content=str(og.get("content") or "") if og else ""
  match=META_PRICE.search(content)
  heading=soup.find("h1")
  base_title=" ".join((heading.get_text(" ",strip=True) if heading else self.config.get("title","")).split())
  unit_node=next((node for node in soup.find_all(["h2","h3","span"]) if re.fullmatch(r"\s*\d+(?:[.,]\d+)?\s*(?:kg|кг|g|гр|г|ml|мл|l|л)\s*",node.get_text(" ",strip=True),re.I)),None)
  unit=" ".join(unit_node.get_text(" ",strip=True).split()) if unit_node else ""
  title=f"{base_title} {unit}".strip()
  if not match:return None,"price_missing"
  price=parse_price_text(match.group(1))
  if not price or price<=0:return None,"zero_price"
  return {**self.config,"original_title":title,"current_price":price,"raw_price_text":match.group(0).strip("· ")},None
