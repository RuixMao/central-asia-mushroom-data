import time
import requests
from openai import OpenAI
from config import AI_API_KEY, AI_PROVIDER
from utils import get_site, log, post_to_site, today_str

PROMPT = """你是中亚食用菌市场分析师，写给中国菌菇出口供应商看。
标题：【中亚菌情】{date}
开头一句话导读（≤25字）
正文3段（每段≤120字）：📊贸易快报；🚛物流看板；💡商机提示（2条可执行建议，每条≤30字）
文末引导关注（≤15字）。输出纯Markdown，不包裹代码块，总字数300-400。不得把缺失值写成0。
数据：
{context}"""

def latest(metric): return get_site(f"/api/ingest/snapshot?metric={metric}&latest=1&limit=50").get("records", [])

def generate(context):
    for attempt in range(3):
        try:
            prompt = PROMPT.format(date=today_str(), context=context)
            if AI_PROVIDER == "claude":
                response = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key":AI_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}, json={"model":"claude-sonnet-4-5","max_tokens":900,"messages":[{"role":"user","content":prompt}]}, timeout=60)
                response.raise_for_status()
                return response.json()["content"][0]["text"].strip()
            client = OpenAI(api_key=AI_API_KEY)
            result = client.responses.create(model="gpt-5-mini", input=prompt)
            return result.output_text.strip()
        except Exception as exc:
            if attempt == 2: raise
            log(f"AI retry {attempt+1}: {exc}"); time.sleep(2 ** attempt)

def run():
    context = f"贸易={latest('trade')}\n物流={latest('logistics')}\n价格={latest('price_retail')}"
    try: body = generate(context)
    except Exception as exc: log(f"report generation failed: {exc}"); return
    plain = body.replace("#", "").replace("*", "")
    summary = plain[:200]
    post_to_site("/api/ingest/report", {"title":f"【中亚菌情】{today_str()}","type":"daily","summary":summary,"body":body,"country":"KZ"})
    post_to_site("/api/ingest/revalidate", {})
if __name__ == "__main__": run()
