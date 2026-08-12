import json
from openai import OpenAI
from config import AI_API_KEY,AI_BASE_URL,AI_MODEL
from utils import get_site,post_to_site,today_str

def run():
 records=get_site("/api/ingest/snapshot?metric=price_retail&latest=1&limit=500").get("records",[])
 today=today_str()
 prices=[r for r in records if r.get("data",{}).get("status")=="live" and r.get("data",{}).get("price_local") is not None and r.get("data",{}).get("observed_at")==today]
 gaps=[r for r in records if r.get("data",{}).get("status")=="gap" and r.get("data",{}).get("observed_at")==today]
 if not prices:
  raise RuntimeError(f"{today} 没有可用价格；采集缺口 {len(gaps)} 条，拒绝生成虚假日报")
 if not AI_API_KEY: raise RuntimeError("AI_API_KEY is not configured")
 context=[{"country":r["country"],"source":r["source"],**r["data"]} for r in prices]
 prompt=f"""你是中亚食用菌市场分析师。仅依据以下 {len(context)} 条今日价格记录生成中文日报，不得加入贸易数据，不得虚构成交价、涨跌幅或缺失价格。
日期：{today}
数据：{json.dumps(context,ensure_ascii=False)}
标题：中亚菌类价格日报｜{today}
正文包括：今日价格全景、国家与渠道观察、商机提示。覆盖全部国家和有效价格，可合并同国同品类价格带。给出2至3条建议，并注明挂牌/页面观察价不等于成交价。输出 Markdown，500至900字。"""
 client=OpenAI(api_key=AI_API_KEY,base_url=AI_BASE_URL or "https://api.deepseek.com")
 result=client.chat.completions.create(model=AI_MODEL or "deepseek-chat",messages=[{"role":"user","content":prompt}],temperature=.2)
 body=(result.choices[0].message.content or "").strip()
 if not body: raise RuntimeError("DeepSeek 未返回日报内容")
 summary=body.replace("#","").replace("*","").replace("\n"," ").strip()[:200]
 post_to_site("/api/ingest/report",{"title":f"中亚菌类价格日报｜{today}","type":"daily","summary":summary,"body":body,"country":"KZ","aiGenerated":True})
 post_to_site("/api/ingest/revalidate",{})
 print(f"DeepSeek 日报生成完成：{len(prices)} 条有效价格，{len(gaps)} 条采集缺口")
if __name__=="__main__": run()
