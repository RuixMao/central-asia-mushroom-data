import datetime as dt
import os
import statistics
import time
import urllib.parse
import requests
from config import SITE_URL, CRON_SECRET

def log(message): print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {message}", flush=True)
def today_str(): return dt.date.today().isoformat()
def median(nums): return statistics.median(nums) if nums else None

# TM 电商源在 GitHub Actions（美国数据中心 IP）被目标站防火墙拒绝。
# 设置环境变量 PROXY_BASE（如 https://tm-proxy.xxx.workers.dev）后，
# 这些域名的请求改经 CF Worker 中转出口；不设置则保持直连（本地正常）。
PROXY_DOMAINS = ("gipertm.com", "asmanexpress.com")

def _maybe_proxy(url, **kwargs):
    base = os.getenv("PROXY_BASE", "").strip().rstrip("/")
    if not base or not any(d in url for d in PROXY_DOMAINS):
        return url, kwargs
    return f"{base}/?url={urllib.parse.quote(url, safe='')}", {}

def safe_get(url, retries=3, backoff=2, **kwargs):
    url, kwargs = _maybe_proxy(url, **kwargs)
    headers = {"User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0 (+data-source-audit)"}
    headers.update(kwargs.pop("headers", {}))
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=25, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            if attempt == retries - 1: log(f"GET failed {url}: {exc}"); return None
            time.sleep(backoff ** attempt)

def post_to_site(endpoint, data, cron_secret=CRON_SECRET, retries=3):
    url = f"{SITE_URL}{endpoint}"
    for attempt in range(retries):
        try:
            response = requests.post(url, json=data, headers={"x-cron-secret": cron_secret}, timeout=30)
            response.raise_for_status()
            result=response.json()
            if result.get("rejected"):
                log(f"POST completed with rejected records: {result.get('errors',[])}")
            return result
        except requests.RequestException as exc:
            if attempt == retries - 1:
                detail=getattr(exc.response,"text","")[:1000] if getattr(exc,"response",None) is not None else ""
                raise RuntimeError(f"POST failed {url}: {exc}; response={detail}") from exc
            time.sleep(2 ** attempt)

def get_site(endpoint):
    response = safe_get(f"{SITE_URL}{endpoint}")
    return response.json() if response else {"records": []}
