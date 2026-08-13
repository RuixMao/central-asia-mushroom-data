import json
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date,timedelta

from openai import OpenAI
from config import AI_API_KEY,AI_BASE_URL,AI_MODEL,TARGET_SPECIES
from utils import get_site,post_to_site,today_str

COUNTRIES={"KZ":"哈萨克斯坦","UZ":"乌兹别克斯坦","KG":"吉尔吉斯斯坦","TJ":"塔吉克斯坦","TM":"土库曼斯坦"}
FORMS={"fresh":"鲜品","chilled":"冷藏","frozen":"冷冻","dried":"干制","pickled":"腌渍","canned":"罐装","powder":"粉剂"}
SECTIONS=("执行摘要","市场趋势与渠道观察","国别政策与新闻信号","情景研判与商机提示","研究口径与风险提示")
FORBIDDEN=re.compile(r"https?://|(?:price|observed|source)\s*[_-]\s*(?:usd|local|cny|at|url)|\b(?:AI|API|JSON|LLM|GPT|ChatGPT|DeepSeek|SQL|D1|null|live|gap|prompt|price_retail)\b|人工智能|大模型|语言模型|模型生成|智能生成|自动生成|机器生成|算法生成|数据库|字段|代码|键值|请求|响应|自动采集|采集管线|采集|抓取|爬虫|入库|接口|算法",re.I)

def customer_safe(body,allowed):
 normalized=unicodedata.normalize("NFKC",body);refs=set(re.findall(r"\[(S\d+)\]",normalized))
 return 900<=len(normalized)<=4200 and "```" not in normalized and "中亚菌类市场研究日报｜" not in normalized and not FORBIDDEN.search(normalized) and all(normalized.count(section)==1 for section in SECTIONS) and refs<=allowed

def summary_from(body):
 paragraphs=[part.strip() for part in re.split(r"\n\s*\n",body) if part.strip() and not re.match(r"^#{1,6}\s",part.strip())]
 return re.sub(r"[#*_>`~-]"," ",paragraphs[0] if paragraphs else body).replace("\n"," ").strip()[:200]

def cell(value):return str(value if value not in (None,"") else "—").replace("|","/").replace("\n"," ").strip()

def run():
 today=today_str();today_date=date.fromisoformat(today);snapshots=get_site("/api/ingest/snapshot?metric=price_retail&limit=500").get("records",[])
 live=[r for r in snapshots if r.get("data",{}).get("status")=="live" and r.get("data",{}).get("normalized_price_usd_per_kg") is not None]
 prices=[r for r in live if r["data"].get("observed_at")==today]
 if not prices:raise RuntimeError(f"{today} 没有标准化可比价格，拒绝生成误导性日报")
 # 同一商品同日去重，避免重复运行把样本量放大。
 latest_prices={}
 for row in prices:
  key=(row["data"].get("product_key") or f'{row.get("country")}:{row.get("source")}:{row["data"].get("original_title")}',today)
  latest_prices.setdefault(key,row)
 prices=list(latest_prices.values())
 table=["| 国家 | 品类（中文/原文） | 渠道（中文/原名） | 形态与规格 | 当地挂牌价 | 折合美元/公斤 | 观察日期 |","|---|---|---|---|---:|---:|---|"]
 for row in prices:
  d=row["data"];table.append(f'| {COUNTRIES.get(row["country"],row["country"])} | {cell(d.get("species_zh"))}（{cell(d.get("original_title"))}） | 当地零售渠道（{cell(d.get("platform_name") or row.get("source"))}） | {FORMS.get(d.get("product_form"),d.get("product_form") or "形态待核验")}；{cell(d.get("package_display"))} | {cell(d.get("price_local"))} {cell(d.get("currency"))} | {float(d["normalized_price_usd_per_kg"]):.2f} | {today} |')
 table_text="\n".join(table)
 history=defaultdict(lambda:defaultdict(list))
 for row in live:
  d=row["data"];observed=d.get("observed_at")
  if not observed:continue
  try:
   if date.fromisoformat(observed)<today_date-timedelta(days=30):continue
  except ValueError:continue
  key=(row["country"],d.get("species_id"),d.get("product_form"));history[key][observed].append(float(d["normalized_price_usd_per_kg"]))
 trends=[]
 for (country,species_id,_),days in history.items():
  ordered=sorted(days.items(),reverse=True);latest=statistics.median(ordered[0][1]);previous=statistics.median(ordered[1][1]) if len(ordered)>1 else None
  trends.append({"国家":COUNTRIES.get(country,country),"品类":TARGET_SPECIES.get(species_id,{}).get("zh",species_id),"有效日期数":len(days),"最新美元每公斤":round(latest,2),"较前次可比变化":f'{(latest/previous-1)*100:.1f}%' if len(days)>=3 and previous else "历史序列不足，暂不判断涨跌"})
 documents=get_site("/api/market-context?days=90").get("records",[])[:25]
 evidence=[]
 for index,doc in enumerate(documents):evidence.append({"id":f"S{index+1}","document_id":doc["id"],"source_type":doc["kind"],"国家":COUNTRIES.get(doc["country"],doc["country"]),"类型":doc["kind"],"标题":doc["title"],"发布机构":doc["publisher"],"发布日期":str(doc["publishedAt"])[:10],"事实摘要":doc["excerpt"],"url":doc["sourceUrl"],"retrieved":str(doc["retrievedAt"])[:10]})
 allowed={item["id"] for item in evidence}
 prompt=f"""你是因恒科技的中亚食用菌首席市场研究员。请写一份面向进口商、渠道商、投资人与经营管理层的中文市场日报。必须像严谨的机构研究简报：先给结论，再解释驱动因素、证据强弱、风险和可执行动作。只可使用下方价格、历史序列和证据包，不得自行补充新闻、政策、数字、来源、因果或预测。
日期：{today}
价格表由系统确定性生成，正文不要抄写全部数字：
{table_text}
同口径历史序列：{json.dumps(trends,ensure_ascii=False)}
已核验政策/新闻/宏观证据包：{json.dumps([{k:v for k,v in item.items() if k not in ('url','retrieved')} for item in evidence],ensure_ascii=False)}

成稿要求：
1. 页面标题另行显示。先写40至80字导读；随后恰好使用“执行摘要”“市场趋势与渠道观察”“国别政策与新闻信号”“情景研判与商机提示”“研究口径与风险提示”五个二级标题。
2. 每个关键句用【事实】【研判】或【情景】标识。事实只复述材料；研判说明推理链；情景必须使用“若…则…”，不能写成确定预测。
3. 政策或新闻事实句必须引用 [S1] 形式的证据编号，且只能使用证据包存在的编号。没有材料的国家写“本期未纳入可核验的新材料”。
4. 趋势只使用有效日期数不少于3的同口径序列；否则写“历史序列不足，暂不判断涨跌”。横向价差只能称“当日价格结构”。
5. 外文专名首次出现用中文名（原文）。给出3至5条含适用对象、触发条件和风险的建议。
6. 不得出现任何生成方式、内部系统、技术字段或流程词。输出900至1800字 Markdown 正文，不附来源清单或网址。"""
 if not AI_API_KEY:raise RuntimeError("AI_API_KEY is not configured")
 client=OpenAI(api_key=AI_API_KEY,base_url=AI_BASE_URL or "https://api.deepseek.com");analysis=""
 for attempt in range(2):
  request=prompt if attempt==0 else f"{prompt}\n\n上一稿未通过发布检查。请仅使用允许的证据编号，保留五个指定栏目后完整重写。"
  result=client.chat.completions.create(model=AI_MODEL or "deepseek-chat",messages=[{"role":"user","content":request}],temperature=.15);analysis=(result.choices[0].message.content or "").strip()
  if customer_safe(analysis,allowed):break
 if not customer_safe(analysis,allowed):raise RuntimeError("日报未通过研究成稿检查，拒绝发布")
 used_ids=set(re.findall(r"\[(S\d+)\]",analysis));used_evidence=[(index,item) for index,item in enumerate(evidence) if item["id"] in used_ids]
 sources="\n".join(f'- [{item["id"]}] [{cell(item["发布机构"])}：{cell(item["标题"])}]({item["url"]})（{item["发布日期"]}，检索于 {item["retrieved"]}）' for _,item in used_evidence) or "- 本期未纳入可核验的新增政策与新闻材料，相关部分不作外推。"
 body=f"{analysis}\n\n## 今日价格全景\n{table_text}\n\n## 来源与资料日期\n{sources}"
 result=post_to_site("/api/ingest/report",{"title":f"中亚菌类市场研究日报｜{today}","type":"daily","summary":summary_from(body),"body":body,"country":"KZ","aiGenerated":True,"sources":[{"evidence_id":item["id"],"document_id":item["document_id"],"source_type":item["source_type"],"title":item["标题"],"url":item["url"],"publisher":item["发布机构"],"published_at":item["发布日期"],"retrieved_at":item["retrieved"]} for _,item in used_evidence]})
 post_to_site("/api/ingest/revalidate",{})
 print(f'市场研究日报完成：{len(prices)} 条标准化价格，{len(evidence)} 条已核验证据，slug={result.get("slug")}')

if __name__=="__main__":run()
