import re,time
from urllib.parse import quote,urljoin
from bs4 import BeautifulSoup
from config import COUNTRIES,VARIETIES,FX_TO_CNY
from utils import log,post_to_site,safe_get,today_str

PRICE_RE=re.compile(r"(\d[\d\s,.]*)\s*(₸|сум|сомони|сом|TMT|KZT|UZS|KGS|TJS)",re.I)
SPEC_RE=re.compile(r"(\d+(?:[.,]\d+)?\s*(?:г|гр|kg|кг|ml|мл|шт))",re.I)

def parse(html,base,variety,channel):
 soup=BeautifulSoup(html,"html.parser"); words=VARIETIES[variety]; keys=[words["ru"].lower(),words.get("uz","").lower()]; rows=[]
 for node in soup.select("article,.product,.product-card,.item,.goods,li")[:160]:
  text=" ".join(node.get_text(" ",strip=True).split()); low=text.lower()
  if not any(k and k in low for k in keys): continue
  match=PRICE_RE.search(text)
  if not match: continue
  value=float(match.group(1).replace(" ","").replace(",",".")); spec=SPEC_RE.search(text); link=node.select_one("a[href]")
  rows.append({"variety":variety,"form":"加工品" if any(x in low for x in ("марин","суш","консерв")) else "鲜品","spec":spec.group(1) if spec else "规格待核","channel":channel,"price_local":value,"source_url":urljoin(base,link.get("href")) if link else base,"status":"live"})
 return rows[:20]

CHANNELS={"arbuz":"生鲜电商","carefood":"批发","flagma_kz":"分类信息","uzum":"综合电商","korzinka":"连锁商超","olx_uz":"分类信息","tegen":"食材批发","globus":"商超","omarket":"本地电商","lalafo":"分类信息","zudbiyor":"即时零售","magnit":"线上商超","somon":"分类信息","tm_market":"本地电商","flagma_tm":"分类信息"}

def run():
 for country,cfg in COUNTRIES.items():
  for variety,words in VARIETIES.items():
   found=[]; keyword=words.get(cfg["lang"],words["ru"])
   for platform,template in cfg["platforms"]:
    url=template.format(q=quote(keyword)); response=safe_get(url)
    if response:
     try: found.extend((platform,row) for row in parse(response.text,url,variety,CHANNELS[platform]))
     except Exception as exc: log(f"parser error {platform}: {exc}")
    time.sleep(1)
   if not found:
    post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":"daily-price-crawler","data":{"variety":variety,"status":"gap","reason":f"未在 {len(cfg['platforms'])} 个平台发现可核验价格","observed_at":today_str()}}); continue
   for platform,row in found:
    row.update({"currency":cfg["currency"],"price_cny":round(row["price_local"]*FX_TO_CNY[cfg["currency"]],2),"observed_at":today_str()})
    post_to_site("/api/ingest/snapshot",{"metric":"price_retail","country":country,"source":platform,"data":row})
 log("今日价格采集完成")
if __name__=="__main__": run()
