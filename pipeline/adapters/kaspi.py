import re
from bs4 import BeautifulSoup
from .render import RenderedProductAdapter
PRICE=re.compile(r"(\d[\d\s]{2,12})\s*₸")
ID_IN_URL=re.compile(r"-(\d+)/?$")
# саңырауқұлақ(哈语"蘑菇")会匹配"蘑菇形电极/蘑菇台灯"等非食品,必须排除
NON_FOOD=re.compile(r"электрод|светильник|лампа|игрушк|украшен|декор|нашлемник|наушник|мангал|форма для|трафарет|саңырауқұлақ тәрізді|электр|ламп",re.I)
class KaspiAdapter(RenderedProductAdapter):
 def parse_rendered(self,html,body=""):
  row,error=self._parse_one(html)
  return (row,None) if row else (None,error)
 def _parse_one(self,html):
  """从渲染 HTML 解析第一个含菌词+价格的商品卡片。"""
  for card in self._cards(html):
   row=self._row_from_card(card)
   if row:return row,None
  return None,"price_missing"
 def _cards(self,html):
  soup=BeautifulSoup(html,"html.parser")
  return soup.select(".item-card,.product-card,[data-product-id]")
 def _row_from_card(self,card):
  text=" ".join(card.get_text(" ",strip=True).split())
  if not re.search(r"шампиньон|вешенк|гриб|саңырауқұлақ|шиитак|эноки|эринги",text,re.I):return None
  if NON_FOOD.search(text):return None
  match=PRICE.search(text)
  if not match:return None
  price=float(match.group(1).replace(" ",""))
  if price<=0:return None
  link=card.find("a",href=True);url=link["href"] if link else self.config["url"]
  if url.startswith("/"):url="https://kaspi.kz"+url
  pid=self.config["platform_product_id"]
  m=ID_IN_URL.search(url)
  if m:pid=f"kaspi-{m.group(1)}"
  return {**self.config,"platform_product_id":pid,"url":url,"original_title":text[:240],"current_price":price,"raw_price_text":match.group(0)}
 def parse_rendered_many(self,html,body=""):
  """返回搜索页上所有含菌词+价格的商品卡片（每条独立 platform_product_id，避免入库互相覆盖）。"""
  rows=[]
  for card in self._cards(html):
   row=self._row_from_card(card)
   if row:rows.append(row)
  return rows
