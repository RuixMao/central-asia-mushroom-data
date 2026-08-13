import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

from utils import log, post_to_site, safe_get

COUNTRIES={
 "KZ":{"name":"Kazakhstan","publisher":"哈萨克斯坦政府及权威机构"},
 "UZ":{"name":"Uzbekistan","publisher":"乌兹别克斯坦政府及权威机构"},
 "KG":{"name":"Kyrgyzstan","publisher":"吉尔吉斯斯坦政府及权威机构"},
 "TJ":{"name":"Tajikistan","publisher":"塔吉克斯坦政府及权威机构"},
 "TM":{"name":"Turkmenistan","publisher":"土库曼斯坦政府及权威机构"},
}
TRUSTED_DOMAINS=("gov.kz","gov.uz","gov.kg","agro.gov.kg","stat.gov.kg","stat.tj","moa.tj","egov.tj","gov.tm","tdh.gov.tm","mfa.gov.tm","fao.org","worldbank.org","un.org","unece.org","eurasiancommission.org")
RELEVANT=re.compile(r"agricultur|food|mushroom|import|export|inflation|retail|logistic|customs|phytosanitary|greenhouse|trade|processing|supply|water|гриб|сельск|продоволь|импорт|экспорт|инфляц|торгов|теплиц|логист|农业|食品|蘑菇|进口|出口|通胀|物流",re.I)
POLICY=re.compile(r"law|decree|regulation|policy|tariff|tax|vat|restriction|subsid|standard|quarantine|закон|указ|постанов|политик|тариф|налог|огранич|субсид|карантин",re.I)

def _feed(country):
 query=f'(agriculture OR food OR mushroom OR import OR inflation OR logistics) {COUNTRIES[country]["name"]} when:45d'
 url=f'https://news.google.com/rss/search?q={quote(query)}&hl=en&gl=US&ceid=US:en'
 response=safe_get(url,retries=2,timeout=35)
 return ET.fromstring(response.content).findall('./channel/item') if response else []

def _domain(item):
 source=item.find('source')
 return ((source.attrib.get('url','') if source is not None else '')+' '+(source.text or '' if source is not None else '')).lower()

def _documents():
 now=datetime.now(timezone.utc);documents=[]
 for country in COUNTRIES:
  for item in _feed(country):
   title=(item.findtext('title') or '').strip();url=(item.findtext('link') or '').strip();domain=_domain(item)
   if not title or not url or not RELEVANT.search(title) or not any(trusted in domain for trusted in TRUSTED_DOMAINS):continue
   try:published=parsedate_to_datetime(item.findtext('pubDate') or '').astimezone(timezone.utc)
   except (TypeError,ValueError):continue
   publisher=(item.findtext('source') or COUNTRIES[country]['publisher']).strip()
   digest=hashlib.sha256(f'{country}|{title}|{url}'.encode('utf-8')).hexdigest()
   documents.append({"id":digest[:32],"country":country,"kind":"policy" if POLICY.search(title) else "news","title":title[:500],"publisher":publisher[:200],"source_url":url,"language":"en","published_at":published.isoformat(),"retrieved_at":now.isoformat(),"excerpt":title[:1000],"primary_source":any(x in domain for x in ("gov.","stat.","fao.org","worldbank.org","un.org","eurasiancommission.org")),"verification_status":"verified","relevance_score":1.0,"content_hash":digest})
   if len([d for d in documents if d['country']==country])>=5:break
 # 世界银行年度通胀仅作为宏观背景，不冒充当日变化。
 wb='https://api.worldbank.org/v2/country/KAZ;UZB;KGZ;TJK;TKM/indicator/FP.CPI.TOTL.ZG?format=json&date=2023:2026&per_page=100'
 response=safe_get(wb,retries=2,timeout=35)
 if response:
  payload=response.json();rows=payload[1] if isinstance(payload,list) and len(payload)>1 else []
  iso={"KAZ":"KZ","UZB":"UZ","KGZ":"KG","TJK":"TJ","TKM":"TM"}
  latest={}
  for row in rows:
   if row.get('value') is not None and row.get('countryiso3code') in iso and row.get('countryiso3code') not in latest:latest[row['countryiso3code']]=row
  for code,row in latest.items():
   country=iso[code];title=f'{row["country"]["value"]} {row["date"]} consumer price inflation';excerpt=f'{row["date"]} consumer price inflation was {float(row["value"]):.2f}% according to the World Bank indicator FP.CPI.TOTL.ZG.';digest=hashlib.sha256(f'{country}|{title}|{wb}'.encode()).hexdigest()
   documents.append({"id":digest[:32],"country":country,"kind":"macro","title":title,"publisher":"World Bank","source_url":f'https://api.worldbank.org/v2/country/{code}/indicator/FP.CPI.TOTL.ZG?format=json',"language":"en","published_at":f'{row["date"]}-12-31T00:00:00+00:00',"retrieved_at":now.isoformat(),"excerpt":excerpt,"primary_source":True,"verification_status":"verified","relevance_score":0.8,"content_hash":digest})
 return documents

def run():
 documents=_documents()
 if not documents:raise RuntimeError('没有取得可核验的市场背景材料')
 result=post_to_site('/api/ingest/market-context',{"documents":documents})
 log(f'市场背景材料完成：写入 {result.get("written",0)} 条，拒绝 {result.get("rejected",0)} 条')

if __name__=='__main__':run()
