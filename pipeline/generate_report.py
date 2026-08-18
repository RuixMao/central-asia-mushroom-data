import json
import os
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date,timedelta

from openai import APIError, AuthenticationError, OpenAI
from config import AI_API_KEY,AI_BASE_URL,AI_MODEL,TARGET_SPECIES
from utils import get_site,log,post_to_site,today_str

COUNTRIES={"KZ":"哈萨克斯坦","UZ":"乌兹别克斯坦","KG":"吉尔吉斯斯坦","TJ":"塔吉克斯坦","TM":"土库曼斯坦"}
FORMS={"fresh":"鲜品","chilled":"冷藏","frozen":"冷冻","dried":"干制","pickled":"腌渍","canned":"罐装","powder":"粉剂"}
SECTIONS=("今日结论","可执行信号","验证清单","商业边界","数据口径")
FORBIDDEN=re.compile(r"https?://|(?:price|observed|source)\s*[_-]\s*(?:usd|local|cny|at|url)|\b(?:AI|API|JSON|LLM|GPT|ChatGPT|DeepSeek|SQL|D1|null|live|gap|prompt|price_retail)\b|人工智能|大模型|语言模型|模型生成|智能生成|自动生成|机器生成|算法生成|数据库|字段|代码|键值|请求|响应|自动采集|采集管线|采集|抓取|爬虫|入库|接口|算法|历史序列不足|暂不判断|暂不提供|暂未直接|数据不足|无足够数据|样本不足|样本量|判断不了|无法判断|不判断涨跌",re.I)
# 品类 → HS 编码（用于把 UN Comtrade 年度进口单价映射到报告品类）
SPECIES_HS={"button_mushroom":"070951","oyster_mushroom":"070959","shiitake":"070959","king_oyster_mushroom":"070959","enoki":"070959","wood_ear":"070959","snow_fungus":"070959","morel":"070959","matsutake":"070959","porcini":"070959","chanterelle":"070959","straw_mushroom":"070959","honey_fungus":"070959","suillus":"070959","truffle":"070959","mixed_mushrooms":"070959","unknown":"070959"}

CUSTOMER_PAIN_GUIDANCE="""
这份日报的目标不是复述数据，而是帮助客户减少试错成本并决定下一步行动。你必须站在客户痛点的位置组织内容：
- 产能方关心卖什么、卖到哪里、价格是否有空间、规格和渠道是否匹配；
- 渠道商关心采购成本、跨平台价差、货源稳定性、补货优先级和异常报价风险；
- 投资者关心市场量级、需求持续性、数据可信度、风险暴露和需要继续验证的关键假设；
- 研究与管理人员关心证据口径、变化是否真实、哪些结论可行动、哪些只能继续观察。

核心洞察应自然串联“客户痛点、可核验证据、业务影响和行动边界”，不要机械重复固定标签。
建议必须具体到适用角色、国家/品类、动作、验证指标和风险边界，不能写“持续关注市场”“加强合作”“把握机遇”等空泛表述。
优先回答：今天相较最近可比观察发生了什么、为什么值得在意、哪些行动具备条件、哪些判断仍需等待。
如果证据只支持观察而不支持决策，要明确写成“验证任务”，不能包装成确定性商机。
语言采用国际机构研究简报常见的克制风格：观点先行、段落连贯、句式简洁、少用口号，不把每一句拆成审计清单。
"""

def customer_safe(body,allowed):
 normalized=unicodedata.normalize("NFKC",body);refs=set(re.findall(r"\[(S\d+)\]",normalized))
 return 500<=len(normalized)<=3200 and "```" not in normalized and "中亚菌类市场研究日报｜" not in normalized and not FORBIDDEN.search(normalized) and all(normalized.count(section)==1 for section in SECTIONS) and refs<=allowed

def summary_from(body):
 paragraphs=[part.strip() for part in re.split(r"\n\s*\n",body) if part.strip() and not re.match(r"^#{1,6}\s",part.strip())]
 plain=re.sub(r"[#*_>`~-]"," ",paragraphs[0] if paragraphs else body).replace("\n"," ").strip()
 return re.split(r"(?<=[。！？])\s*",plain)[0][:160]

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
  except ValueError:continue
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

def decision_fallback(today,signals,evidence):
 actionable=[item for item in signals if item["状态"]=="可行动"];verify=[item for item in signals if item["状态"]=="待核验"]
 conclusion=(f"今天发现 {len(actionable)} 项值得立即核实的价格变化。" if actionable else "今天没有发现需要立即调整采购、报价或产能计划的市场变化，建议维持现有安排。")
 lines=[f'- **{item["状态"]}｜{item["国家"]}·{item["品类"]}**：{item["判断"]} 证据：{item["证据"]}' for item in (actionable+verify)[:5]] or ["- 今日未出现同商品连续报价变化或同规格多渠道价差，维持观察。"]
 return f"""本期只比较页面明确标注重量、形态一致的商品；规格来源不清或价差异常的记录不进入市场判断。
## 今日结论
- {conclusion}
- 零售挂牌价只用于筛选询价对象，不能直接视为成交价、需求或利润。
- 在取得批量报价、可售净重、税费和物流报价前，不给出毛利判断。
## 可执行信号
{chr(10).join(lines)}
## 验证清单
- 确认商品是否在售、是否促销、可售净重、产地与最小订货量；核心规格不一致即停止价格比较。
- 取得同规格批量报价及有效期，再补充运输、损耗、关税和渠道费用；缺少其中一项不进入利润测算。
- 只有同一商品连续三次有效观察，或同规格获得两个独立渠道确认，才升级为小批量试单候选。
## 商业边界
本期不把包装差异、加工形态差异或渠道定位差异解释为套利空间。没有询盘、销量或库存证据的价格变化，不外推为需求增长。
## 数据口径
数据为公开在线零售挂牌价并统一换算为美元/公斤，不等同于批发成交价、到岸成本或终端销量。报告用于缩小验证范围，不替代真实询价和供应链核算。"""

def cell(value):return str(value if value not in (None,"") else "—").replace("|","/").replace("\n"," ").strip()

def run():
 today=today_str();today_date=date.fromisoformat(today);snapshots=get_site("/api/ingest/snapshot?metric=price_retail&limit=500").get("records",[])
 existing=get_site("/api/ingest/report?type=daily").get("records",[])
 revision=os.environ.get("REPORT_REVISION", "").lower() in {"1","true","yes"}
 if not revision and any(today in str(report.get("title", "")) for report in existing):
  print(f"{today} 日报已存在，跳过重复生成")
  return
 live=[r for r in snapshots if r.get("data",{}).get("status")=="live" and r.get("data",{}).get("normalized_price_usd_per_kg") is not None and r.get("data",{}).get("package_source") in {"page_title","page_structured_data"}]
 prices=[r for r in live if r["data"].get("observed_at")==today]
 if not prices:raise RuntimeError(f"{today} 没有标准化可比价格，拒绝生成误导性日报")
 # 同一商品同日去重，避免重复运行把样本量放大。
 latest_prices={}
 for row in prices:
  key=(row["data"].get("product_key") or f'{row.get("country")}:{row.get("source")}:{row["data"].get("original_title")}',today)
  latest_prices.setdefault(key,row)
 prices=list(latest_prices.values())
 signals=build_signals(prices,live,today_date)
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
 evidence=[]
 for index,doc in enumerate(documents):evidence.append({"id":f"S{index+1}","document_id":doc["id"],"source_type":doc["kind"],"国家":COUNTRIES.get(doc["country"],doc["country"]),"类型":doc["kind"],"标题":doc["title"],"发布机构":doc["publisher"],"发布日期":str(doc["publishedAt"])[:10],"事实摘要":doc["excerpt"],"url":doc["sourceUrl"],"retrieved":str(doc["retrievedAt"])[:10]})
 allowed={item["id"] for item in evidence}
 prompt=f"""你是因恒科技的中亚食用菌首席市场研究员。请写一份面向进口商、渠道商、投资人与经营管理层的中文决策简报。客户为减少验证成本和错误决策付费，不为报价复述或通用建议付费。只可使用下方价格、结构化信号和证据包，不得自行补充新闻、政策、数字、来源、因果、利润或预测。
{CUSTOMER_PAIN_GUIDANCE}
日期：{today}
价格表由系统确定性生成，正文不要抄写全部数字：
{table_text}
同口径零售历史序列：{json.dumps(trends,ensure_ascii=False)}
结构化商业信号（正文判断只能从这里选择，不得把其他价差写成机会）：{json.dumps(signals,ensure_ascii=False)}
年度进口单价参考（贸易口径，UN Comtrade）：{json.dumps(annual_ref,ensure_ascii=False)}
已核验政策/新闻/宏观证据包：{json.dumps([{k:v for k,v in item.items() if k not in ('url','retrieved')} for item in evidence],ensure_ascii=False)}

成稿要求：
1. 页面标题另行显示。先写50至90字导读；随后恰好使用“今日结论”“可执行信号”“验证清单”“商业边界”“数据口径”五个二级标题。正文500至1200字；没有新增信号时宁可短写，不得凑篇幅。
2. “今日结论”最多3条，只回答今天出现了什么、是否达到行动门槛、客户现在应做或不应做什么。严禁逐国罗列报价、中位数和渠道数。
3. “可执行信号”逐条写明国家、品类、形态、规格、渠道、变化或价差、证据强度、商业意义和停止条件。若结构化商业信号为空，写“今天没有发现需要立即调整采购、报价或产能计划的市场变化”，不得使用“可执行价格信号”等内部研究术语，也不得制造商机。
4. 政策或新闻事实必须引用 [S1] 形式的证据编号，且只能使用证据包存在的编号。没有材料时简洁说明“本期未纳入可核验的新材料”，不要逐国重复。
5. 零售趋势只使用有效日期数不少于3的同口径序列；不足3期的品类可用“年度进口单价参考（贸易口径）”描述年度走势，并注明其不是零售价；两种依据均不足的品类不写趋势。禁止出现“历史序列不足”“暂不判断”“数据不足”“无法判断”等表述。
6. “验证清单”必须是业务人员可执行的询价字段与通过门槛，包括在售/促销状态、净重、等级、产地、最小订货量、报价有效期、物流、损耗、税费和渠道费用；不得使用“持续关注”“加强合作”等空话。
7. “商业边界”必须区分挂牌价、成交价、到岸成本、需求和利润。没有真实询盘、批量报价和完整成本时，不得给出利润、需求增长或扩产结论。
8. 政策信号只陈述可核验事实。不得出现任何生成方式、内部系统、技术字段或流程词。输出 Markdown 正文，不附来源清单或网址。"""
 if not AI_API_KEY:raise RuntimeError("AI_API_KEY is not configured")
 client=OpenAI(api_key=AI_API_KEY,base_url=AI_BASE_URL or "https://api.deepseek.com");analysis="";used_fallback=False
 try:
  for attempt in range(2):
   request=prompt if attempt==0 else f"{prompt}\n\n上一稿未通过发布检查。请仅使用允许的证据编号，保留五个指定栏目，以连贯、克制的机构研究语言完整重写。"
   result=client.chat.completions.create(model=AI_MODEL or "deepseek-v4-flash",messages=[{"role":"user","content":request}],temperature=.15,max_tokens=5000,extra_body={"thinking":{"type":"disabled"}});analysis=clean_analysis(result.choices[0].message.content or "")
   if customer_safe(analysis,allowed):break
 except (AuthenticationError,APIError) as exc:
  log(f"DeepSeek unavailable, using verified fallback: {type(exc).__name__}")
  analysis=clean_analysis(decision_fallback(today,signals,evidence));used_fallback=True
 if not used_fallback and not customer_safe(analysis,allowed):
  log("模型稿未通过研究成稿检查，改用已核验研究模板")
  analysis=clean_analysis(decision_fallback(today,signals,evidence));used_fallback=True
 if not customer_safe(analysis,allowed):raise RuntimeError("日报未通过研究成稿检查，拒绝发布")
 used_ids=set(re.findall(r"\[(S\d+)\]",analysis));used_evidence=[(index,item) for index,item in enumerate(evidence) if item["id"] in used_ids]
 sources="\n".join(f'- [{item["id"]}] [{cell(item["发布机构"])}：{cell(item["标题"])}]({item["url"]})（{item["发布日期"]}，检索于 {item["retrieved"]}）' for _,item in used_evidence) or "- 本期未纳入可核验的新增政策与新闻材料，相关部分不作外推。"
 body=f"{analysis}\n\n## 今日价格全景\n{table_text}\n\n## 来源与资料日期\n{sources}"
 title=f"中亚菌类市场研究日报｜{today}"
 result=post_to_site("/api/ingest/report",{"title":title,"type":"daily","summary":summary_from(body),"body":body,"country":"KZ","aiGenerated":True,"sources":[{"evidence_id":item["id"],"document_id":item["document_id"],"source_type":item["source_type"],"title":item["标题"],"url":item["url"],"publisher":item["发布机构"],"published_at":item["发布日期"],"retrieved_at":item["retrieved"]} for _,item in used_evidence]})
 post_to_site("/api/ingest/revalidate",{})
 print(f'市场研究日报完成：{len(prices)} 条标准化价格，{len(evidence)} 条已核验证据，slug={result.get("slug")}')

if __name__=="__main__":run()
