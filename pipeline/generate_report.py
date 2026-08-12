import json
import time

import requests
from openai import OpenAI

from config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_PROVIDER
from utils import get_site, log, post_to_site, today_str

PROMPT = """你是中亚食用菌市场分析师，报告写给中国食用菌出口供应商。
标题：【中亚菌情】{date}
开头一句话导读（不超过25字）。
正文分为三部分：贸易快报、物流看板、商机提示。
商机提示给出2条可执行建议，每条不超过30字。
文末给出一句不超过15字的持续关注提示。
输出纯 Markdown，总字数200—400字。不得把缺失值写成0。
数据：{context}"""


def latest(metric):
    return get_site(f"/api/ingest/snapshot?metric={metric}&latest=1&limit=50").get("records", [])


def provider_settings():
    provider = AI_PROVIDER.lower().strip()
    if provider == "deepseek":
        return AI_BASE_URL or "https://api.deepseek.com", AI_MODEL or "deepseek-v4-flash"
    return AI_BASE_URL or None, AI_MODEL or "gpt-5-mini"


def generate(context):
    if not AI_API_KEY:
        raise RuntimeError("AI_API_KEY is not configured")
    for attempt in range(3):
        try:
            prompt = PROMPT.format(date=today_str(), context=json.dumps(context, ensure_ascii=False))
            if AI_PROVIDER.lower().strip() == "claude":
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": AI_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": AI_MODEL or "claude-sonnet-4-5", "max_tokens": 900, "messages": [{"role": "user", "content": prompt}]},
                    timeout=60,
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"].strip()
            base_url, model = provider_settings()
            client = OpenAI(api_key=AI_API_KEY, base_url=base_url)
            request = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            if AI_PROVIDER.lower().strip() == "deepseek":
                request["extra_body"] = {"thinking": {"type": "disabled"}}
            result = client.chat.completions.create(**request)
            return (result.choices[0].message.content or "").strip()
        except Exception as exc:
            if attempt == 2:
                raise
            log(f"AI retry {attempt + 1}: {exc}")
            time.sleep(2 ** attempt)


def baseline_report(context):
    counts = {name: len(records) for name, records in context.items()}
    return f"""今日自动采集已完成，AI 服务暂不可用，以下为规则生成的基线简报。

## 贸易快报
本期读取到贸易记录 {counts['trade']} 条。缺失数据保持缺失，不按零值处理；市场规模判断以已核验官方记录为准。

## 物流看板
本期读取到物流记录 {counts['logistics']} 条。暂无可靠新增信号时沿用最近一次已验证状态，避免将接口异常误判为市场变化。

## 商机提示
1. 优先核验有新增报价的国家与菌种。
2. 将挂牌价与贸易量变化交叉比对。

持续关注下一次采集。"""


def run():
    context = {
        "trade": latest("trade"),
        "logistics": latest("logistics"),
        "price": latest("price_retail"),
    }
    ai_generated = True
    try:
        body = generate(context)
        if not body:
            raise RuntimeError("AI returned an empty report")
    except Exception as exc:
        log(f"report generation failed, using baseline: {exc}")
        body = baseline_report(context)
        ai_generated = False
    plain = body.replace("#", "").replace("*", "")
    post_to_site(
        "/api/ingest/report",
        {
            "title": f"【中亚菌情】{today_str()}",
            "type": "daily",
            "summary": plain[:200],
            "body": body,
            "country": "KZ",
            "aiGenerated": ai_generated,
        },
    )
    post_to_site("/api/ingest/revalidate", {})


if __name__ == "__main__":
    run()
