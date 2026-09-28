import json
import os
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import APIError, AuthenticationError, OpenAI
from config import AI_API_KEY,AI_BASE_URL,AI_MODEL,TARGET_SPECIES
from sanity import check_usd_per_kg, review_sanity_outliers
from utils import delete_from_site,get_site,log,post_to_site

COUNTRIES={"KZ":"哈萨克斯坦","UZ":"乌兹别克斯坦","KG":"吉尔吉斯斯坦","TJ":"塔吉克斯坦","TM":"土库曼斯坦","LA":"老挝","VN":"越南","TH":"泰国","MM":"缅甸","KH":"柬埔寨"}
FORMS={"fresh":"鲜品","chilled":"冷藏","frozen":"冷冻","dried":"干制","pickled":"腌渍","canned":"罐装","powder":"粉剂"}
SPECIES_NAMES={"button_mushroom":"双孢菇","oyster_mushroom":"平菇","shiitake":"香菇","enoki":"金针菇","shimeji":"真姬菇","porcini":"牛肝菌","suillus":"乳牛肝菌","morel":"羊肚菌","chanterelle":"鸡油菌","king_oyster_mushroom":"杏鲍菇","wood_ear":"木耳"}
CENTRAL_ASIA=("KZ","UZ","KG","TJ","TM")
SOUTHEAST_ASIA=("LA","VN","TH","MM","KH")
REPORT_SPECIES_PRIORITY=("oyster_mushroom","shiitake","wood_ear","king_oyster_mushroom","enoki","button_mushroom","shimeji")
SECTIONS=("今日要点","市场动态","机会与风险","行动建议","数据说明")
FORBIDDEN=re.compile(r"https?://|(?:price|observed|source)\s*[_-]\s*(?:usd|local|cny|at|url)|\b(?:AI|API|JSON|LLM|GPT|ChatGPT|DeepSeek|SQL|D1|null|live|gap|prompt|price_retail|n\s*=)\b|人工智能|大模型|语言模型|模型生成|智能生成|自动生成|机器生成|算法生成|数据库|字段|代码|键值|请求|响应|自动采集|采集管线|抓取|爬虫|入库|接口|算法|置信度|离散度|无事件窗口|Executive Summary|样本量|口径|样本有限|报价有限|数据有限|仅作参考|仅供参考|只用于发现询价线索|自动复核|已核验材料|检索到\s*\d+\s*条材料|经核验|有效参考价|有效报价|有效观察|不作外推|不据此判断整体涨跌|不直接推导批发利润|本报告暂不|给老板|给采购|给外贸|来源与资料日期|待进一步确认|待确认的价格|原因待确认|原因待查|详见正文|详见上表",re.I)
# 品类 → HS 编码（用于把 UN Comtrade 年度进口单价映射到报告品类）
SPECIES_HS={"button_mushroom":"070951","oyster_mushroom":"070959","shiitake":"070959","king_oyster_mushroom":"070959","enoki":"070959","wood_ear":"070959","snow_fungus":"070959","morel":"070959","matsutake":"070959","porcini":"070959","chanterelle":"070959","straw_mushroom":"070959","honey_fungus":"070959","suillus":"070959","truffle":"070959","mixed_mushrooms":"070959","unknown":"070959"}

CUSTOMER_PAIN_GUIDANCE="""
你是因恒科技的中亚及东南亚食用菌市场研究日报主编，为微信公众号撰写面向老板、外贸负责人和采购负责人的每日市场文章。读者要在3分钟内看清今天发生了什么、要不要行动。东南亚覆盖老挝、越南、泰国、缅甸、柬埔寨；老挝为首要拓展市场，在当日事实满足发布门禁时优先呈现，但不得预设正面结论。

最高原则：给客户看成品，不给客户看后厨。只呈现结论、价格、规格、渠道、事实依据、建议和风险；不得出现采集过程、复核动作、材料数量、样本统计、数据质量自评和方法说明。能判断就用数字说清楚，不能判断的内容直接省略。
采用行业垂直媒体风格：专业但不装腔。结论先行，短段短句，一段不超过3行，关键结论加粗。同一信息只出现一次，免责边界只放文末数据说明。
品类统一使用中文规范名，清除评价数、分期文案和营销语；鲜品、干品、冷冻、腌渍分开呈现。精品或小包装必须在品类后标注规格。
行动建议固定使用“决策参考、采购落地、报价规范”三个栏目，引用当日具体数据，使用“建议、应”等规范语气，不用“给老板、给采购、给外贸”。
涉及土库曼斯坦写明海关透明度低、许可获取难度高，谨慎进入；涉及鸡枞写明仅适合华人小众圈层，不建议作为主力出口品类。
所有判断只能来自提供的价格和事实，严禁虚构数据、事件、因果、需求、利润或预测。
"""

def customer_safe(body,allowed):
 normalized=unicodedata.normalize("NFKC",body);refs=set(re.findall(r"\[(S\d+)\]",normalized))
 return 500<=len(normalized)<=2000 and "```" not in normalized and "食用菌出海市场日报｜" not in normalized and not FORBIDDEN.search(normalized) and not re.search(r"\|\s*(?:食用菌|菌类)\s*\|",normalized) and all(normalized.count(section)==1 for section in SECTIONS) and refs<=allowed

def covers_today_sea_markets(body,prices):
 """Every Southeast Asian market with report-ready prices must be discussed in prose."""
 required={COUNTRIES[row["country"]] for row in prices if row.get("country") in {"LA","VN","TH","MM","KH"}}
 return all(name in body for name in required)

def utf8_truncate(text,max_bytes):
 encoded=text.encode("utf-8")
 if len(encoded)<=max_bytes:return text
 return encoded[:max_bytes].decode("utf-8","ignore").rstrip("：:，,。 、|")

def customer_visible_price(row):
 """客户版只接收品种、规格和价格均完整且已确认的记录。"""
 d=row.get("data",{})
 return d.get("status")=="live" and d.get("validation_status","valid")=="valid" and d.get("cross_validation_status","verified")=="verified" and not d.get("sanity_outlier") and d.get("species_id") in SPECIES_NAMES and d.get("package_display") not in (None,"") and d.get("normalized_price_usd_per_kg") is not None and d.get("price_local") is not None and d.get("currency") and d.get("package_source") in {"page_title","page_structured_data"}

def select_report_prices(live,today,max_age_days=7):
 """Use today's qualified rows, then add each missing SEA market's latest qualified rows."""
 today_date=date.fromisoformat(today);selected=[row for row in live if row.get("data",{}).get("observed_at")==today]
 covered={row.get("country") for row in selected}
 for code in SOUTHEAST_ASIA:
  if code in covered:continue
  recent=[]
  for row in live:
   if row.get("country")!=code:continue
   observed=row.get("data",{}).get("observed_at")
   try:observed_date=date.fromisoformat(str(observed))
   except (TypeError,ValueError):continue
   if today_date-timedelta(days=max_age_days)<=observed_date<=today_date:recent.append(row)
  if not recent:continue
  latest=max(row["data"]["observed_at"] for row in recent)
  latest_rows=[row for row in recent if row["data"]["observed_at"]==latest]
  latest_rows.sort(key=lambda row:(REPORT_SPECIES_PRIORITY.index(row["data"].get("species_id")) if row["data"].get("species_id") in REPORT_SPECIES_PRIORITY else len(REPORT_SPECIES_PRIORITY),float(row["data"]["normalized_price_usd_per_kg"])))
  representatives=[];species=set()
  for row in latest_rows:
   species_id=row["data"].get("species_id")
   if species_id in species:continue
   representatives.append(row);species.add(species_id)
   if len(representatives)==2:break
  selected.extend(representatives)
 return selected

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

def title_from(today,body,prices=None,recent_titles=None):
 day=date.fromisoformat(today);headline="市场平稳无异常"
 rows=[]
 for row in prices or []:
  d=row.get("data",{})
  if d.get("observed_at") not in (None,today):continue
  try:value=float(d["normalized_price_usd_per_kg"])
  except (KeyError,TypeError,ValueError):continue
  if value<=0 or d.get("species_id") not in SPECIES_NAMES:continue
  rows.append((row,value))

 # 先生成多个可复算的当日看点，再避开上一期已经使用的标题。
 grouped=defaultdict(list)
 for row,value in rows:grouped[row["data"]["species_id"]].append((row,value))
 candidates=[]
 for species_id,items in grouped.items():
  values=[value for _,value in items]
  if len(values)>=2 and min(values)>0:
   candidates.append((max(values)/min(values),f"{SPECIES_NAMES[species_id]}价差{max(values)/min(values):.1f}倍"))
 candidates.sort(key=lambda item:item[0],reverse=True)
 headlines=[text for _,text in candidates]
 if rows:
  high_row,high_value=max(rows,key=lambda item:item[1])
  high_data=high_row["data"]
  headlines.append(f"{COUNTRIES.get(high_row.get('country'),high_row.get('country',''))}{SPECIES_NAMES[high_data['species_id']]}报价{high_value:.1f}美元")
  countries={row.get("country") for row,_ in rows if row.get("country")}
  headlines.append(f"{len(countries)}国{len(grouped)}个品种价格更新")
 previous=str((recent_titles or [""])[0])
 headline=next((item for item in headlines if item and item not in previous),headlines[0] if headlines else headline)
 if headline=="市场平稳无异常":
  match=re.search(r"\*\*(?:\d+[.、]\s*)?([^*。！？]{8,25})[。！？]?\*\*",body)
  if match:headline=match.group(1).strip("：:，,。 ")
 prefix=f"食用菌出海市场日报｜{day.month}月{day.day}日："
 return prefix+utf8_truncate(headline,64-len(prefix.encode("utf-8")))

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
- {today} 的可比观察覆盖中亚及东南亚目标市场，共形成 {len(prices)} 条标准化报价，来自 {len(platforms)} 个渠道。
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

def decision_fallback(today,prices,evidence):
 ordered=sorted(prices,key=lambda r:float(r["data"]["normalized_price_usd_per_kg"]))
 low,high=ordered[0],ordered[-1];ld,hd=low["data"],high["data"]
 low_country=COUNTRIES.get(low["country"],low["country"]);high_country=COUNTRIES.get(high["country"],high["country"])
 low_name=SPECIES_NAMES[ld["species_id"]];high_name=SPECIES_NAMES[hd["species_id"]]
 low_channel=ld.get("platform_name") or low.get("source");high_channel=hd.get("platform_name") or high.get("source")
 buttons=[r for r in prices if r["data"].get("species_id")=="button_mushroom" and r["data"].get("product_form")=="fresh"]
 button_low=min(buttons,key=lambda r:float(r["data"]["normalized_price_usd_per_kg"])) if buttons else low
 bd=button_low["data"];button_country=COUNTRIES.get(button_low["country"],button_low["country"]);button_channel=bd.get("platform_name") or button_low.get("source")
 today_events=[item for item in evidence if item.get("发布日期")==today]
 event_line=(f'今日新增事件为“{today_events[0]["标题"]}”[{today_events[0]["id"]}]，建议按该事实评估受影响环节。' if today_events else "今日无新增政策与事件，市场面平稳。")
 tm=[r for r in prices if r.get("country")=="TM"]
 tm_line=(f'土库曼斯坦{SPECIES_NAMES[tm[0]["data"]["species_id"]]}在{tm[0]["data"].get("platform_name") or tm[0].get("source")}报价{float(tm[0]["data"]["normalized_price_usd_per_kg"]):.2f}美元/公斤；该国海关透明度低、许可获取难度高，谨慎进入。' if tm else "")
 sea_lines=[]
 for code in ("LA","VN","TH","MM","KH"):
  rows=[r for r in prices if r.get("country")==code]
  if not rows:continue
  best=min(rows,key=lambda r:float(r["data"]["normalized_price_usd_per_kg"]));data=best["data"]
  sea_lines.append(f'- **{COUNTRIES[code]}：**{data.get("platform_name") or best.get("source")}的{SPECIES_NAMES[data["species_id"]]}（{data.get("package_display")}装）为{float(data["normalized_price_usd_per_kg"]):.2f}美元/公斤，观察日期{data.get("observed_at")}；建议以同规格批量询价验证渠道空间。')
 sea_text="\n".join(sea_lines)
 return f"""## 今日要点

1. **本期展示报价从{float(ld["normalized_price_usd_per_kg"]):.2f}至{float(hd["normalized_price_usd_per_kg"]):.2f}美元/公斤，价差主要来自品类与规格。**建议只在同品类、同形态、同净重条件下比价。
2. **{button_country}{bd.get("package_display")}装双孢菇在{button_channel}报价{float(bd["normalized_price_usd_per_kg"]):.2f}美元/公斤。**建议采购端据此询问批量价格、库存和最小起订量。
3. **{event_line}**{'建议维持现有出货节奏。' if not today_events else '建议核对现有出货安排。'}
4. **{tm_line or '今日各市场按已确认报价正常跟踪。'}**

## 市场动态

**本期低价为{low_country}{low_name}，高价为{high_country}{high_name}，两者品类与规格不同，不作直接比较。**

{event_line}

**东南亚近期渠道价格：**

{sea_text}

## 机会与风险

- **询价机会：**{low_country}{low_channel}的{low_name}（{ld.get("package_display")}装）报价{float(ld["normalized_price_usd_per_kg"]):.2f}美元/公斤。建议先索取同规格批量报价、库存和最小起订量，条件齐全后再考虑试单。
- **价格误判风险：**{high_country}{high_channel}的{high_name}（{hd.get("package_display")}装）报价{float(hd["normalized_price_usd_per_kg"]):.2f}美元/公斤。若忽略品类、规格和渠道差异直接倒推利润，可能造成报价失真和库存积压。
{f'- **清关风险：**{tm_line}建议发货前核实许可和代理资质，避免货到口岸后无法清关。' if tm else ''}

## 行动建议

- **决策参考：**建议今日不因{high_country}{high_name}{float(hd["normalized_price_usd_per_kg"]):.2f}美元/公斤的零售报价调整整体备货，应先按同品类和同规格核算。
- **采购落地：**建议向{button_country}{button_channel}询问{bd.get("package_display")}装双孢菇的批量报价、库存、最小起订量和交货期。
- **报价规范：**{low_country}{low_name}{float(ld["normalized_price_usd_per_kg"]):.2f}美元/公斤与{high_country}{high_name}{float(hd["normalized_price_usd_per_kg"]):.2f}美元/公斤不可直接比较；报价单应分开列示品类、形态、净重和等级。

## 数据说明

本报告价格来自中亚及东南亚目标市场主流零售与电商渠道公开挂牌价，统一折算为美元/公斤。零售挂牌价与批发成交价、到岸成本存在差异，正式决策请以批量报价为准。数据来源：因恒科技监测，采集日期 {today}。如需核验具体报价来源，可联系专属客服索取。"""

def cell(value):return str(value if value not in (None,"") else "—").replace("|","/").replace("\n"," ").strip()

def package_kg(display):
 match=re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(kg|g)\b",str(display or ""),re.I)
 if not match:return None
 value=float(match.group(1));return value if match.group(2).lower()=="kg" else value/1000

def report_publication_date(report):
 """Use the Shanghai publication day; old slugs are a fallback, not title text.

 The API serializes publishedAt as an ISO timestamp from the UTC database value.
 Slugs contain a UTC date, so a valid timestamp must take precedence at midnight.
 """
 value=report.get("publishedAt")
 try:
  if isinstance(value,(int,float)) and not isinstance(value,bool):
   published=datetime.fromtimestamp(value/1000,tz=timezone.utc)
  elif isinstance(value,str) and value.strip():
   published=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
   if published.tzinfo is None:published=published.replace(tzinfo=timezone.utc)
  else:published=None
  if published is not None:return published.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
 except (ValueError,TypeError,OverflowError,OSError):pass
 match=re.match(r"^(\d{4}-\d{2}-\d{2})(?:-|$)",str(report.get("slug") or ""))
 if match:
  try:return date.fromisoformat(match.group(1)).isoformat()
  except ValueError:pass
 return None


def run():
 today=datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
 existing=get_site("/api/ingest/report?type=daily").get("records",[])
 revision=os.environ.get("REPORT_REVISION", "").lower() in {"1","true","yes"}
 current=next((report for report in existing if report_publication_date(report)==today),None)
 artifact_output=os.environ.get("REPORT_ARTIFACT_OUTPUT","").strip()
 preview_output=os.environ.get("REPORT_PREVIEW_OUTPUT","").strip()
 if not revision and current:
  if artifact_output:
   artifact_path=Path(artifact_output);artifact_path.parent.mkdir(parents=True,exist_ok=True)
   artifact_path.write_text(json.dumps({**{key:current.get(key,"") for key in ("title","summary","body","slug")},"date":today},ensure_ascii=False),encoding="utf-8")
  if preview_output:
   preview_path=Path(preview_output);preview_path.parent.mkdir(parents=True,exist_ok=True)
   preview_path.write_text(f'# {current["title"]}\n\n{current["body"]}\n',encoding="utf-8")
  print(f"{today} 日报已存在，跳过重复生成")
  return

 from report_release import build_customer_report, customer_price_is_eligible, validate_customer_report
 snapshots=get_site("/api/ingest/snapshot?metric=price_retail&limit=500").get("records",[])
 if not any(customer_price_is_eligible(row,today) for row in snapshots):
  raise RuntimeError(f"{today} 没有可用于客户版的已确认价格，拒绝生成误导性日报")
 # A busy country must not evict another country's current observations from the global page.
 covered={row.get("country") for row in snapshots if customer_price_is_eligible(row,today)}
 for country in COUNTRIES:
  if country not in covered:
   snapshots.extend(get_site(f"/api/ingest/snapshot?metric=price_retail&country={country}&limit=200").get("records",[]))
 documents=get_site("/api/market-context?days=1").get("records",[])
 report=build_customer_report(today,snapshots,[row.get("title","") for row in existing],official_events=documents)
 validate_customer_report(report,today)
 title,body,summary=report["title"],report["body"],report["summary"]
 if preview_output:
  preview_path=Path(preview_output);preview_path.parent.mkdir(parents=True,exist_ok=True)
  preview_path.write_text(f"# {title}\n\n{body}\n",encoding="utf-8")
  result={}
 else:
  result=post_to_site("/api/ingest/report",{"title":title,"type":"daily","summary":summary,"body":body,"country":"KZ","aiGenerated":False,"sources":report.get("sources",[])})
  if not result.get("slug"):raise RuntimeError("Report publication returned no slug")
  confirmed=get_site("/api/ingest/report?type=daily").get("records",[])
  if not any(row.get("slug")==result["slug"] and row.get("body")==body for row in confirmed):
   raise RuntimeError("Published report could not be confirmed by read-back")
  replace_slugs=[slug.strip() for slug in os.environ.get("REPORT_REPLACE_SLUG","").split(",") if slug.strip()]
  for replace_slug in dict.fromkeys(replace_slugs):
   if replace_slug!=result["slug"]:delete_from_site(f"/api/ingest/report?slug={replace_slug}")
  post_to_site("/api/ingest/revalidate",{})
 if artifact_output:
  artifact_path=Path(artifact_output);artifact_path.parent.mkdir(parents=True,exist_ok=True)
  artifact_path.write_text(json.dumps({"title":title,"summary":summary,"body":body,"slug":result.get("slug"),"date":today},ensure_ascii=False),encoding="utf-8")
 print(f'{"日报预览完成（未发布）" if preview_output else "市场研究日报完成"}：{len(report["prices"])} 条当日价格，slug={result.get("slug","")}')

if __name__=="__main__":run()
