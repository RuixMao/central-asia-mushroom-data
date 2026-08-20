import json
import os
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date,timedelta
from pathlib import Path

from openai import APIError, AuthenticationError, OpenAI
from config import AI_API_KEY,AI_BASE_URL,AI_MODEL,TARGET_SPECIES
from sanity import check_usd_per_kg, review_sanity_outliers
from utils import get_site,log,post_to_site,today_str

COUNTRIES={"KZ":"哈萨克斯坦","UZ":"乌兹别克斯坦","KG":"吉尔吉斯斯坦","TJ":"塔吉克斯坦","TM":"土库曼斯坦"}
FORMS={"fresh":"鲜品","chilled":"冷藏","frozen":"冷冻","dried":"干制","pickled":"腌渍","canned":"罐装","powder":"粉剂"}
SPECIES_NAMES={"button_mushroom":"双孢菇","oyster_mushroom":"平菇","shiitake":"香菇","enoki":"金针菇","shimeji":"真姬菇","porcini":"牛肝菌","suillus":"乳牛肝菌","morel":"羊肚菌","chanterelle":"鸡油菌","king_oyster_mushroom":"杏鲍菇","wood_ear":"木耳"}
SECTIONS=("今日要点","市场动态","机会与风险","行动建议","数据说明")
FORBIDDEN=re.compile(r"https?://|(?:price|observed|source)\s*[_-]\s*(?:usd|local|cny|at|url)|\b(?:AI|API|JSON|LLM|GPT|ChatGPT|DeepSeek|SQL|D1|null|live|gap|prompt|price_retail|n\s*=)\b|人工智能|大模型|语言模型|模型生成|智能生成|自动生成|机器生成|算法生成|数据库|字段|代码|键值|请求|响应|自动采集|采集管线|抓取|爬虫|入库|接口|算法|置信度|离散度|无事件窗口|Executive Summary|样本量|口径|样本有限|报价有限|数据有限|仅作参考|仅供参考|只用于发现询价线索|自动复核|已核验材料|检索到\s*\d+\s*条材料|经核验|有效参考价|有效报价|有效观察|不作外推|不据此判断整体涨跌|不直接推导批发利润|本报告暂不|给老板|给采购|给外贸|来源与资料日期",re.I)
# 品类 → HS 编码（用于把 UN Comtrade 年度进口单价映射到报告品类）
SPECIES_HS={"button_mushroom":"070951","oyster_mushroom":"070959","shiitake":"070959","king_oyster_mushroom":"070959","enoki":"070959","wood_ear":"070959","snow_fungus":"070959","morel":"070959","matsutake":"070959","porcini":"070959","chanterelle":"070959","straw_mushroom":"070959","honey_fungus":"070959","suillus":"070959","truffle":"070959","mixed_mushrooms":"070959","unknown":"070959"}

CUSTOMER_PAIN_GUIDANCE="""
你是因恒科技的中亚食用菌市场研究日报主编，为微信公众号撰写面向老板、外贸负责人和采购负责人的每日市场文章。读者要在3分钟内看清今天发生了什么、要不要行动。

最高原则：给客户看成品，不给客户看后厨。只呈现结论、价格、规格、渠道、事实依据、建议和风险；不得出现采集过程、复核动作、材料数量、样本统计、数据质量自评和方法说明。能判断就用数字说清楚，不能判断的内容直接省略。
采用行业垂直媒体风格：专业但不装腔。结论先行，短段短句，一段不超过3行，关键结论加粗。同一信息只出现一次，免责边界只放文末数据说明。
品类统一使用中文规范名，清除评价数、分期文案和营销语；鲜品、干品、冷冻分开呈现。精品或小包装必须在品类后标注规格。
行动建议固定使用“决策参考、采购落地、报价规范”三个栏目，引用当日具体数据，使用“建议、应”等规范语气，不用“给老板、给采购、给外贸”。
涉及土库曼斯坦写明海关透明度低、许可获取难度高，谨慎进入；涉及鸡枞写明仅适合华人小众圈层，不建议作为主力出口品类。
所有判断只能来自提供的价格和事实，严禁虚构数据、事件、因果、需求、利润或预测。
"""

def customer_safe(body,allowed):
 normalized=unicodedata.normalize("NFKC",body);refs=set(re.findall(r"\[(S\d+)\]",normalized))
 return 500<=len(normalized)<=2000 and "```" not in normalized and "中亚菌类市场研究日报｜" not in normalized and not FORBIDDEN.search(normalized) and all(normalized.count(section)==1 for section in SECTIONS) and refs<=allowed

def summary_from(body):
 paragraphs=[part.strip() for part in re.split(r"\n\s*\n",body) if part.strip() and not re.match(r"^#{1,6}\s",part.strip())]
 plain=re.sub(r"[#*_>`~-]"," ",paragraphs[0] if paragraphs else body).replace("\n"," ").strip()
 return re.split(r"(?<=[。！？])\s*",plain)[0][:160]

def display_usd_per_kg(value):
 """价格缺失时保留记录并显示破折号，避免待确认记录中断整份日报。"""
 try:
  return f"{float(value):.2f}" if value is not None else "—"
 except (TypeError,ValueError):
  return "—"

def title_from(today,body):
 day=date.fromisoformat(today);match=re.search(r"\*\*(?:\d+[.、]\s*)?([^*。！？]{8,55})[。！？]?\*\*",body)
 headline=(match.group(1).strip("：:，,。 ") if match else "市场价格与风险提示")
 return f"中亚食用菌市场日报｜{day.month}月{day.day}日：{headline}"

def clean_analysis(body):
 lines=body.strip().splitlines()
 while lines and not lines[0].strip():lines.pop(0)
 if lines and re.match(r"^#\s+.*日报\s*$",lines[0].strip()):lines.pop(0)
 while lines and not lines[0].strip():lines.pop(0)
 if lines and re.match(r"^\*\*日期[:：].+\*\*$",lines[0].strip()):lines.pop(0)
 while lines and not lines[0].strip():lines.pop(0)
 if lines and lines[0].strip()=="## 导读":lines.pop(0)
 return "\n".join(lines).strip()

def verified_fallback(today,prices,trends,evidence):
 country_groups=defaultdict(list);platforms=set()
 for row in prices:
  data=row["data"];country_groups[row["country"]].append(float(data["normalized_price_usd_per_kg"]));platforms.add(data.get("platform_name") or row.get("source"))
 country_lines=[]
 for country,values in sorted(country_groups.items()):
  country_lines.append(f'- {COUNTRIES.get(country,country)}：{len(values)} 条可比报价，样本中位数 {statistics.median(values):.2f} 美元/公斤。')
 trend_lines=[]
 for item in trends[:5]:
  change=item.get("较前次可比变化")
  trend_lines.append(f'- {item.get("国家")} {item.get("品类")}：最新 {item.get("最新美元每公斤")} 美元/公斤' + (f'，较前次 {change}' if change else '，本期列为验证任务') + '。')
 if not trend_lines:trend_lines=['- 本期仅呈现当日可比报价，不把跨品类价差解释为趋势。']
 evidence_note=f'本期纳入 {len(evidence)} 条已核验外部材料。' if evidence else '本期未纳入可核验的新增政策与新闻材料，相关部分不作外推。'
 return f"""今日价格信号整体平稳，但跨市场价差仍需回到品类、形态与规格三个维度理解。与其追逐单一低价，更值得关注的是哪些市场已经具备多渠道验证条件，以及哪些报价能够进入真实询盘。

## 核心观点
- {today} 的可比观察覆盖中亚五国，共形成 {len(prices)} 条标准化报价，来自 {len(platforms)} 个渠道。
- 多数跨市场价差仍包含包装、加工形态和渠道定位差异，不能直接解释为利润空间。
- 当前更适合推进规格核验和到岸成本测算，而非仅凭零售挂牌价扩大采购或产能安排。

## 市场变化与驱动
{chr(10).join(country_lines)}
{chr(10).join(trend_lines)}
价格分化主要由商品形态、包装净重和渠道定位共同驱动。对价差较大的商品，应先核对净重、鲜/干/腌制形态、产地、促销和库存状态，再进入采购或销售测算。

## 商业含义
产能方可优先筛选已有多渠道报价的市场，围绕明确规格测试接受度；渠道商可把异常价差转化为询价线索，并同步确认真实采购量、账期和补货频率；投资者应把覆盖连续性与价格复核结果纳入市场判断，而非用单日高价推断需求规模。

## 关注事项
- 若同一国家、同一品类连续三次出现多渠道有效报价，且规格一致，可启动小批量报价验证。
- 若价差主要来自包装、加工形态或促销状态，应停止跨平台直接比较。
- {evidence_note}没有可核验证据支持的政策、需求或项目变化，不作为当期商业判断依据。

## 数据口径与风险
本报告使用在线零售商品观察价并统一换算为美元/公斤，不代表批发成交价、到岸成本或终端实际销量。汇率、促销、缺货、包装换算和分类误差均可能影响比较结果。报告用于缩小验证范围，具体决策仍需结合商品规格、库存、物流、关税和真实询盘。"""

def build_signals(prices,live,today_date):
 today=today_date.isoformat();by_product=defaultdict(dict)
 for row in live:
  d=row["data"];observed=d.get("observed_at");key=d.get("product_key")
  if not key or not observed:continue
  try:
   if date.fromisoformat(observed)<today_date-timedelta(days=30):continue
  except (TypeError,ValueError):continue
  by_product[key][observed]=float(d["normalized_price_usd_per_kg"])
 signals=[]
 for row in prices:
  d=row["data"];key=d.get("product_key");days=sorted(by_product.get(key,{}),reverse=True)
  if len(days)<2 or days[0]!=today:continue
  latest=by_product[key][days[0]];previous=by_product[key][days[1]]
  change=(latest/previous-1)*100 if previous else 0
  if abs(change)<3:continue
  status="可行动" if len(days)>=3 and abs(change)>=10 else "待核验"
  signals.append({"状态":status,"类型":"同商品连续变化","国家":COUNTRIES.get(row["country"],row["country"]),"品类":d.get("species_zh") or d.get("species_id"),"形态":FORMS.get(d.get("product_form"),d.get("product_form")),"规格":d.get("package_display") or "待核验","渠道":d.get("platform_name") or row.get("source"),"最新美元每公斤":round(latest,2),"变化":f"{change:+.1f}%","判断":f'同一商品较前次变化 {change:+.1f}%，应先核对促销与库存状态。',"证据":f'{len(days)} 个有效观察日；商品标识保持一致。',"停止条件":"商品规格、促销状态或在售状态发生变化"})
 comparable=defaultdict(list)
 for row in prices:
  d=row["data"];spec=(d.get("package_display") or "").strip().lower()
  if not spec:continue
  comparable[(row["country"],d.get("species_id"),d.get("product_form"),spec)].append(row)
 for rows in comparable.values():
  channels={r["data"].get("platform_name") or r.get("source") for r in rows}
  if len(channels)<2:continue
  values=[float(r["data"]["normalized_price_usd_per_kg"]) for r in rows];low=min(values);high=max(values);spread=(high/low-1)*100 if low else 0
  if spread<15 or spread>100:continue
  sample=rows[0];d=sample["data"]
  signals.append({"状态":"待核验","类型":"同规格渠道价差","国家":COUNTRIES.get(sample["country"],sample["country"]),"品类":d.get("species_zh") or d.get("species_id"),"形态":FORMS.get(d.get("product_form"),d.get("product_form")),"规格":d.get("package_display"),"渠道":"、".join(sorted(channels)),"最新美元每公斤":f"{low:.2f}–{high:.2f}","变化":f"价差 {spread:.1f}%","判断":f'同规格多渠道挂牌价差 {spread:.1f}%，可转为批量询价线索，但尚不能视为利润空间。',"证据":f'{len(channels)} 个独立渠道、同日同规格报价。',"停止条件":"净重、产地、等级、促销或库存状态不一致"})
 return signals

def build_market_facts(prices):
 groups=defaultdict(list)
 for row in prices:
  d=row["data"];groups[(row["country"],d.get("species_id"),d.get("product_form"))].append(row)
 facts=[];dispersions=[]
 for (country,species_id,form),rows in groups.items():
  values=[float(r["data"]["normalized_price_usd_per_kg"]) for r in rows];med=statistics.median(values)
  facts.append({"国家":COUNTRIES.get(country,country),"品类":TARGET_SPECIES.get(species_id,{}).get("zh",species_id),"形态":FORMS.get(form,form),"中位价USD/kg":round(med,2),"样本量":len(values),"最低":round(min(values),2),"最高":round(max(values),2)})
  if len(values)>=2 and min(values)>0 and max(values)/min(values)>=2:
   low=min(rows,key=lambda r:float(r["data"]["normalized_price_usd_per_kg"]));high=max(rows,key=lambda r:float(r["data"]["normalized_price_usd_per_kg"]))
   dispersions.append({"国家":COUNTRIES.get(country,country),"品类":TARGET_SPECIES.get(species_id,{}).get("zh",species_id),"形态":FORMS.get(form,form),"低价USD/kg":round(min(values),2),"低价规格":low["data"].get("package_display"),"低价渠道":low["data"].get("platform_name") or low.get("source"),"高价USD/kg":round(max(values),2),"高价规格":high["data"].get("package_display"),"高价渠道":high["data"].get("platform_name") or high.get("source"),"倍数":round(max(values)/min(values),1),"样本量":len(values),"判定":"规格或渠道溢价待核验，不得解释为批发套利空间","置信度":"中"})
 return {"分国家品类形态统计":facts,"同国同品类异常离散":sorted(dispersions,key=lambda x:x["倍数"],reverse=True)}

def decision_fallback(today,signals,evidence,market_facts,trends,review_prices):
 facts=sorted(market_facts["分国家品类形态统计"],key=lambda x:(-x["样本量"],x["国家"]))
 sample_lines=[f'- **{item["国家"]}{item["品类"]}{item["形态"]}：{item["中位价USD/kg"]:.2f}美元/公斤。**' for item in facts[:5]]
 review_line=""
 if review_prices:
  d=max(review_prices,key=lambda r:float(r["data"].get("normalized_price_usd_per_kg") or 0))["data"]
  reason=d.get("sanity_review_reason") or d.get("sanity_reason") or "具体原因待查"
  if d.get("sanity_review_status")=="explained":
   review_line=f'**{d.get("species_zh") or "菌类"}（精品）报价为{float(d["normalized_price_usd_per_kg"]):.2f}美元/公斤。**{reason.replace("自动复核：","")}；建议与普通大包装分开比价。'
  else:
   review_line=f'**{d.get("species_zh") or "菌类"}{float(d["normalized_price_usd_per_kg"]):.2f}美元/公斤，原因待进一步确认。**建议确认规格后再用于比价。'
 else:review_line="**今日价格未见突出异常。**建议维持现有采购与出货节奏。"
 review_action="精品小包装价格应标明规格和档次，不与普通大包装直接比较。" if review_prices and all(r.get("data",{}).get("sanity_review_status")=="explained" for r in review_prices) else "规格或档次未确认的价格不用于对客报价。"
 event_line="今日无新增政策与事件，市场面平稳。" if not evidence else "今日政策与市场事件详见正文事实条目。"
 return f"""## 今日要点

1. {review_line}
2. **今日价格重点见鲜品、干品和冷冻分表。**建议按相同形态、净重和等级进行比较。
3. **{event_line}**建议维持现有出货节奏。
4. **土库曼斯坦仍需谨慎进入。**当地海关透明度低、许可获取难度高，企业应先核实准入和清关成本。

## 市场动态

**今日价格差异主要来自国家、品类、形态和包装规格。**

{chr(10).join(sample_lines) if sample_lines else '- 今日无新增价格。'}

{event_line}

## 机会与风险

- **询价机会：**若低价渠道能够持续提供同规格、同等级商品，可向该渠道索取批量报价和最小起订量；只有报价有效期、库存和交货条件齐全后，才考虑试单。
- **价格误判风险：**小包装、高端商品、促销或运费可能显著抬高折算单价。未经核实直接倒推利润，可能造成报价失真和库存积压。
- **清关风险：**进入土库曼斯坦前必须先核实许可和代理资质，避免货物到口岸后无法正常清关。

## 行动建议

- **决策参考：**建议不因单条精品小包装价格调整整体备货。
- **采购落地：**建议针对今日低价品类询问批量报价、最小起订量、库存和交货期。
- **报价规范：**跨渠道比价前应核对净重、等级、形态和产地；{review_action}

## 数据说明

本报告价格来自中亚五国主流零售与电商渠道公开挂牌价，统一折算为美元/公斤。零售挂牌价与批发成交价、到岸成本存在差异，正式决策请以批量报价为准。数据来源：因恒科技监测，采集日期 {today}。"""

def cell(value):return str(value if value not in (None,"") else "—").replace("|","/").replace("\n"," ").strip()

def package_kg(display):
 match=re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(kg|g)\b",str(display or ""),re.I)
 if not match:return None
 value=float(match.group(1));return value if match.group(2).lower()=="kg" else value/1000

def run():
 today=today_str();today_date=date.fromisoformat(today);snapshots=get_site("/api/ingest/snapshot?metric=price_retail&limit=500").get("records",[])
 existing=get_site("/api/ingest/report?type=daily").get("records",[])
 revision=os.environ.get("REPORT_REVISION", "").lower() in {"1","true","yes"}
 if not revision and any(today in str(report.get("title", "")) for report in existing):
  print(f"{today} 日报已存在，跳过重复生成")
  return
 # 兼容尚未写入 sanity 字段的历史快照：生成前再次校验，并用同日规格做二次复核。
 review_candidates=[]
 for row in snapshots:
  d=row.get("data",{});value=d.get("normalized_price_usd_per_kg")
  if d.get("status")!="live" or value is None:continue
  d.setdefault("validation_status","valid")
  sanity=check_usd_per_kg(d.get("species_id"),row.get("country"),value)
  if sanity["sanity_outlier"]:
   d.update(sanity);d["validation_status"]="needs_review"
  review_candidates.append({"country":row.get("country"),**d,"normalized_quantity_kg":package_kg(d.get("package_display"))})
 review_sanity_outliers(review_candidates)
 for item in review_candidates:
  if not item.get("sanity_outlier"):continue
  for row in snapshots:
   d=row.get("data",{})
   if row.get("country")==item.get("country") and d.get("product_key")==item.get("product_key"):
    d["sanity_review_status"]=item.get("sanity_review_status");d["sanity_review_reason"]=item.get("sanity_review_reason");d["sanity_reason"]=item.get("sanity_reason")
 live=[r for r in snapshots if r.get("data",{}).get("status")=="live" and r.get("data",{}).get("validation_status","valid")=="valid" and not r.get("data",{}).get("sanity_outlier") and r.get("data",{}).get("normalized_price_usd_per_kg") is not None and r.get("data",{}).get("package_source") in {"page_title","page_structured_data"}]
 review_prices=[r for r in snapshots if r.get("data",{}).get("status")=="live" and (r.get("data",{}).get("validation_status")=="needs_review" or r.get("data",{}).get("sanity_outlier")) and r.get("data",{}).get("observed_at")==today]
 specialty_prices=[r for r in review_prices if r.get("data",{}).get("sanity_review_status")=="explained"]
 pending_review_prices=[r for r in review_prices if r not in specialty_prices]
 prices=[r for r in live if r["data"].get("observed_at")==today]
 if not prices and not review_prices:raise RuntimeError(f"{today} 没有标准化价格记录，拒绝生成误导性日报")
 # 同一商品同日去重，避免重复运行把样本量放大。
 latest_prices={}
 for row in prices:
  key=(row["data"].get("product_key") or f'{row.get("country")}:{row.get("source")}:{row["data"].get("original_title")}',today)
  latest_prices.setdefault(key,row)
 prices=list(latest_prices.values())
 signals=build_signals(prices,live,today_date)
 market_facts=build_market_facts(prices)
 table_groups=defaultdict(list)
 for row in prices+specialty_prices:
  d=row["data"];form=d.get("product_form") or "other";name=SPECIES_NAMES.get(d.get("species_id"),d.get("species_zh") or "食用菌");spec=cell(d.get("package_display"));premium=row in specialty_prices
  product=f'{name}（精品{spec}装）' if premium else f'{name}（{spec}装）'
  table_groups[form].append(f'| {COUNTRIES.get(row["country"],row["country"])} | {product} | {cell(d.get("platform_name") or row.get("source"))} | {cell(d.get("price_local"))} {cell(d.get("currency"))} | {float(d["normalized_price_usd_per_kg"]):.2f} | {today} |')
 table_parts=[]
 for form in ("fresh","dried","frozen","chilled","pickled","canned","other"):
  if form not in table_groups:continue
  label={"fresh":"鲜品","dried":"干品","frozen":"冷冻","chilled":"冷藏","pickled":"腌渍","canned":"罐装","other":"其他"}[form]
  table_parts.append("\n".join([f"### {label}","","| 国家 | 品类（中文，注明规格） | 渠道 | 当地挂牌价 | 折合美元/公斤 | 观察日期 |","|---|---|---|---:|---:|---:|",*table_groups[form]]))
 table_text="\n\n".join(table_parts)
 review_table_text=""
 if pending_review_prices:
  review_table=["| 国家 | 品类 | 渠道 | 规格 | USD/kg | 说明 |","|---|---|---|---|---:|---|"]
  for row in pending_review_prices:
   d=row["data"];review_table.append(f'| {COUNTRIES.get(row["country"],row["country"])} | {cell(SPECIES_NAMES.get(d.get("species_id"),d.get("species_zh") or "食用菌"))} | {cell(d.get("platform_name") or row.get("source"))} | {cell(d.get("package_display"))} | {display_usd_per_kg(d.get("normalized_price_usd_per_kg"))} | 原因待进一步确认 |')
  review_table_text="\n\n### 待进一步确认的价格\n\n"+"\n".join(review_table)
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
  trends.append({"国家":COUNTRIES.get(country,country),"品类":TARGET_SPECIES.get(species_id,{}).get("zh",species_id),"有效日期数":len(days),"最新美元每公斤":round(latest,2),"较前次可比变化":f'{(latest/previous-1)*100:.1f}%' if len(days)>=3 and previous else None})
 # 年度进口单价（贸易口径，UN Comtrade）历史序列：供零售序列不足的品类做年度趋势参考
 trade_rows=get_site("/api/ingest/snapshot?metric=trade&limit=500").get("records",[])
 annual_by_country_hs=defaultdict(dict)
 for r in trade_rows:
  d=r.get("data",{})
  if d.get("status")!="live" or d.get("period_type")=="monthly":continue
  year=d.get("year");unit=d.get("unit_price_usd_kg");hs=d.get("hs")
  if year and unit is not None and hs:
   annual_by_country_hs[(r.get("country"),hs)][str(year)]=float(unit)
 annual_ref=[]
 for (country,species_id,form),days in history.items():
  hs=SPECIES_HS.get(species_id or "unknown")
  seq=annual_by_country_hs.get((country,hs)) if hs else None
  seq=seq or {}
  if len(seq)>=2:
   years=sorted(seq);first=seq[years[0]];last=seq[years[-1]]
   change=f"{(last/first-1)*100:.1f}%" if first else None
   annual_ref.append({"国家":COUNTRIES.get(country,country),"品类":TARGET_SPECIES.get(species_id,{}).get("zh",species_id),"贸易口径年度进口单价USD/kg":{y:seq[y] for y in years},"多年变化":change})
 documents=get_site("/api/market-context?days=90").get("records",[])[:25]
 calendar=get_site(f"/api/ingest/snapshot?metric=event_calendar&year={today_date.year}&limit=1000").get("records",[])
 upcoming_events=[]
 for row in calendar:
  d=row.get("data",{})
  try:start=date.fromisoformat(str(d.get("start_date")));end=date.fromisoformat(str(d.get("end_date")))
  except (TypeError,ValueError):continue
  if end>=today_date and start<=today_date+timedelta(days=7):upcoming_events.append({"国家":COUNTRIES.get(row.get("country"),row.get("country")),"事件":d.get("name_zh"),"开始":d.get("start_date"),"结束":d.get("end_date"),"业务影响":d.get("business_impact"),"物流影响":d.get("logistics_impact")})
 evidence=[]
 for index,doc in enumerate(documents):evidence.append({"id":f"S{index+1}","document_id":doc["id"],"source_type":doc["kind"],"国家":COUNTRIES.get(doc["country"],doc["country"]),"类型":doc["kind"],"标题":doc["title"],"发布机构":doc["publisher"],"发布日期":str(doc["publishedAt"])[:10],"事实摘要":doc["excerpt"],"url":doc["sourceUrl"],"retrieved":str(doc["retrievedAt"])[:10]})
 allowed={item["id"] for item in evidence}
 review_findings=[{"国家":COUNTRIES.get(row["country"],row["country"]),"品类":f'{row["data"].get("species_zh") or row["data"].get("species_id")}（精品）' if row in specialty_prices else row["data"].get("species_zh") or row["data"].get("species_id"),"规格":row["data"].get("package_display"),"美元每公斤":row["data"].get("normalized_price_usd_per_kg"),"复核结论":row["data"].get("sanity_review_reason") or row["data"].get("sanity_reason") or "具体原因待查"} for row in review_prices]
 prompt=f"""你是因恒科技的中亚食用菌首席市场研究员。请写一份面向进口商、渠道商、投资人与经营管理层的中文决策简报。客户为减少验证成本和错误决策付费，不为报价复述或通用建议付费。只可使用下方价格、结构化信号和证据包，不得自行补充新闻、政策、数字、来源、因果、利润或预测。
{CUSTOMER_PAIN_GUIDANCE}
日期：{today}
价格表由系统确定性生成，正文不要抄写全部数字：
{table_text}
同口径零售历史序列：{json.dumps(trends,ensure_ascii=False)}
结构化商业信号（正文判断只能从这里选择，不得把其他价差写成机会）：{json.dumps(signals,ensure_ascii=False)}
确定性市场统计与异常离散（必须分析，不得忽略）：{json.dumps(market_facts,ensure_ascii=False)}
精品小包装及待复核价格（精品价格应正常展示并标注“精品”，但与普通大包装分开比较）：{json.dumps(review_findings,ensure_ascii=False)}
年度进口单价参考（贸易口径，UN Comtrade）：{json.dumps(annual_ref,ensure_ascii=False)}
已核验政策/新闻/宏观证据包：{json.dumps([{k:v for k,v in item.items() if k not in ('url','retrieved')} for item in evidence],ensure_ascii=False)}
未来7天官方节日事件（只有列表非空时才可写入正文）：{json.dumps(upcoming_events,ensure_ascii=False)}

成稿要求：
1. 正文写500至1400字，恰好使用“今日要点”“市场动态”“机会与风险”“行动建议”“数据说明”五个二级标题，适合微信公众号手机阅读。
2. “今日要点”写3至5条，每条采用“结论+具体数字或事实+是否行动”的客户语言；老板只读本节就能知道今天发生了什么、要不要动。
3. 禁止出现样本有限、报价有限、仅供参考、自动复核、已核验材料、检索数量、不作外推等后台或自我否定表达。能确认的用数字直接写，不能确认的内容省略。
4. 鲜品、干品、冷冻和盐渍分开点评。只有同品类同形态至少3条有效报价且连续覆盖至少5个交易日，才可写趋势或涨跌；否则不得输出指数和强趋势结论。
5. 已确认是小包装的高价作为正常精品价格展示，品类后标注“（精品Xg装）”，说明是规格溢价并与普通大包装分开比较；不得描述后台复核过程。其余存疑价格不进入主流价和机会判断，没有明确依据时写“原因待进一步确认”。
6. 政策或新闻事实必须引用 [S1] 形式的证据编号；无新增事件时写“今日无新增政策、海关、物流事件，市场面平稳”，并说明是否需要调整出货安排。
7. 机会与风险必须具体到国家、品类、触发条件、潜在损失和规避动作。行动建议固定用“决策参考、采购落地、报价规范”三个栏目，引用当日价格，使用“建议、应”等语气。
8. 涉及土库曼斯坦写明其海关透明度低、许可获取难度高，谨慎进入；涉及鸡枞写明其仅适合华人小众圈层，不建议作为主力出口。
9. “数据说明”简洁说明零售挂牌价、美元/公斤折算、样本限制及采集日期。不得虚构批发价、物流价、政策、原因、利润或需求。输出标准 Markdown，不重复输出完整明细表或网址，后续程序会附加。"""
 preview_output=os.environ.get("REPORT_PREVIEW_OUTPUT","").strip()
 if not AI_API_KEY and not preview_output:raise RuntimeError("AI_API_KEY is not configured")
 client=OpenAI(api_key=AI_API_KEY,base_url=AI_BASE_URL or "https://api.deepseek.com") if AI_API_KEY else None;analysis="";used_fallback=False
 try:
  if client is None:raise RuntimeError("preview fallback")
  for attempt in range(2):
   request=prompt if attempt==0 else f"{prompt}\n\n上一稿未通过发布检查。请仅使用允许的证据编号，严格保留五个公众号栏目；删除所有内部研究术语，用客户听得懂的短句和当日数字完整重写。"
   result=client.chat.completions.create(model=AI_MODEL or "deepseek-v4-flash",messages=[{"role":"user","content":request}],temperature=.15,max_tokens=5000,extra_body={"thinking":{"type":"disabled"}});analysis=clean_analysis(result.choices[0].message.content or "")
   if customer_safe(analysis,allowed):break
 except (AuthenticationError,APIError,RuntimeError) as exc:
  log(f"DeepSeek unavailable, using verified fallback: {type(exc).__name__}")
  analysis=clean_analysis(decision_fallback(today,signals,evidence,market_facts,trends,review_prices));used_fallback=True
 if not used_fallback and not customer_safe(analysis,allowed):
  log("模型稿未通过成稿检查，改用固定日报模板")
  analysis=clean_analysis(decision_fallback(today,signals,evidence,market_facts,trends,review_prices));used_fallback=True
 if not customer_safe(analysis,allowed):raise RuntimeError("日报未通过研究成稿检查，拒绝发布")
 used_ids=set(re.findall(r"\[(S\d+)\]",analysis));used_evidence=[(index,item) for index,item in enumerate(evidence) if item["id"] in used_ids]
 marker="\n## 数据说明"
 market_marker="\n## 机会与风险"
 if market_marker in analysis:
  before_risk,after_risk=analysis.split(market_marker,1);analysis=f"{before_risk}\n\n{table_text}{market_marker}{after_risk}"
 if marker in analysis:
  main_text,data_note=analysis.split(marker,1);body=f"{main_text}{review_table_text}{marker}{data_note}"
 else:body=f"{analysis}{review_table_text}"
 # 公众号版只有在同品类同形态连续覆盖达到门槛时才展示趋势；当前不自动附加内部指数表。
 title=title_from(today,analysis)
 if preview_output:
  preview_path=Path(preview_output)
  preview_path.parent.mkdir(parents=True,exist_ok=True)
  preview_path.write_text(f"# {title}\n\n{body}\n",encoding="utf-8")
  print(f"日报预览已生成（未发布）：{preview_path}")
  return
 summary=summary_from(body)
 result=post_to_site("/api/ingest/report",{"title":title,"type":"daily","summary":summary,"body":body,"country":"KZ","aiGenerated":True,"sources":[{"evidence_id":item["id"],"document_id":item["document_id"],"source_type":item["source_type"],"title":item["标题"],"url":item["url"],"publisher":item["发布机构"],"published_at":item["发布日期"],"retrieved_at":item["retrieved"]} for _,item in used_evidence]})
 artifact_output=os.environ.get("REPORT_ARTIFACT_OUTPUT","").strip()
 if artifact_output:
  artifact_path=Path(artifact_output)
  artifact_path.parent.mkdir(parents=True,exist_ok=True)
  artifact_path.write_text(json.dumps({"title":title,"summary":summary,"body":body,"slug":result.get("slug"),"date":today},ensure_ascii=False),encoding="utf-8")
 post_to_site("/api/ingest/revalidate",{})
 print(f'市场研究日报完成：{len(prices)} 条标准化价格，{len(evidence)} 条已核验证据，slug={result.get("slug")}')

if __name__=="__main__":run()
