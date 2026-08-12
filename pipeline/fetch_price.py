import json,re
from bs4 import BeautifulSoup
from config import FX_TO_CNY
from utils import log,post_to_site,safe_get,today_str

SOURCES=[
 {"country":"KG","source":"Globus Online","url":"https://globus-online.kg/ru-kg/good/9905ed980f9d469888dadc3efc68b6fe000200010000","variety":"双孢菇","form":"鲜品","spec":"1kg","channel":"商超","currency":"KGS"},
 {"country":"KG","source":"Globus Online","url":"https://globus-online.kg/ru-kg/catalog/grocery/category/f65c13b6fb5ffb8c5752ff03be5a71bd/a0e91ee087e645b98fb1698163a1c64f000200010000","variety":"平菇","form":"鲜品","spec":"1kg","channel":"商超","currency":"KGS","name_contains":"Вешен"},
 {"country":"KG","source":"O!Market","url":"https://market.o.kg/ru/bishkek/produkty-pitanija/ovoschi-frukty/product/4450008b-61fc-4fb7-839f-c4bdd5669c5c/griby-shampinony-1kg","variety":"双孢菇","form":"鲜品","spec":"300g","channel":"本地电商","currency":"KGS"},
 {"country":"TJ","source":"Zudbiyor","url":"https://zudbiyor.tj/product/141","variety":"双孢菇","form":"鲜品","spec":"1kg","channel":"即时零售","currency":"TJS"},
 {"country":"TJ","source":"Magnit.tj","url":"https://magnit.tj/product/show/18786","variety":"双孢菇","form":"鲜品","spec":"250g","channel":"商超电商","currency":"TJS"},
 {"country":"TJ","source":"Magnit.tj","url":"https://magnit.tj/product/show/16839","variety":"平菇","form":"鲜品","spec":"500g","channel":"商超电商","currency":"TJS"},
]

PRICE_PATTERNS=[
 re.compile(r"(\d[\d\s]*(?:[.,]\d+)?)\s*(?:сомони|сом(?:/кг)?|с\b)",re.I),
 re.compile(r'"price"\s*:\s*"?(\d+(?:[.,]\d+)?)',re.I),
]

def clean_text(html):
 return " ".join(BeautifulSoup(html,"html.parser").get_text(" ",strip=True).split())

def find_price(html,source):
 text=clean_text(html); marker=source.get("name_contains")
 if marker:
  pos=text.lower().find(marker.lower())
  if pos<0:return None
  text=text[pos:pos+500]
 for pattern in PRICE_PATTERNS:
  match=pattern.search(text)
  if match:
   value=float(match.group(1).replace(" ","").replace(",","."))
   if value>0:return value
 return None

def publish_gap(source,reason):
 post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":source["country"],"source":source["source"],"data":{"variety":source["variety"],"status":"gap","reason":reason,"observed_at":today_str(),"source_url":source["url"]}})

def run():
 live=0; gaps=0
 for source in SOURCES:
  response=safe_get(source["url"],retries=1)
  if not response:
   publish_gap(source,"商品页无法访问");gaps+=1;continue
  price=find_price(response.text,source)
  if price is None:
   publish_gap(source,"商品页未发现可核验的正价格");gaps+=1;continue
  row={key:source[key] for key in ("variety","form","spec","channel","currency")}
  row.update({"price_local":price,"price_cny":round(price*FX_TO_CNY[source["currency"]],2),"observed_at":today_str(),"source_url":source["url"],"status":"live"})
  post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":source["country"],"source":source["source"],"data":row});live+=1
 log(f"今日价格采集完成：有效 {live} 条，缺口 {gaps} 条")
 if not live: raise RuntimeError("今日没有采集到任何有效价格")

if __name__=="__main__":run()
