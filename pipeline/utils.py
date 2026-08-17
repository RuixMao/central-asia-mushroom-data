import datetime as dt
import os
import statistics
import time
import urllib.parse
import threading
import requests
from config import SITE_URL, CRON_SECRET

DATA_API_URL = os.environ.get("DATA_API_URL", "").rstrip("/")
DATA_SYNC_SECRET = os.environ.get("DATA_SYNC_SECRET", "")

def log(message): print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {message}", flush=True)
def today_str(): return dt.date.today().isoformat()
def median(nums): return statistics.median(nums) if nums else None

# TM 电商源在 GitHub Actions（美国数据中心 IP）被目标站防火墙拒绝。
# 设置环境变量 PROXY_BASE（如 https://tm-proxy.xxx.workers.dev）后，
# 这些域名的请求改经 CF Worker 中转出口；不设置则保持直连（本地正常）。
PROXY_DOMAINS = ("gipertm.com", "asmanexpress.com")
_LAST_REQUEST_BY_HOST = {}
_REQUEST_LOCK = threading.Lock()
MIN_REQUEST_INTERVAL = 1.5

def _maybe_proxy(url, **kwargs):
    base = os.getenv("PROXY_BASE", "").strip().rstrip("/")
    if not base or not any(d in url for d in PROXY_DOMAINS):
        return url, kwargs
    return f"{base}/?url={urllib.parse.quote(url, safe='')}", {}

def safe_get(url, retries=3, backoff=2, **kwargs):
    url, kwargs = _maybe_proxy(url, **kwargs)
    headers = {"User-Agent": "Mozilla/5.0 YinhengMarketResearch/1.0 (+data-source-audit)"}
    headers.update(kwargs.pop("headers", {}))
    # 代理转发路径（CF Worker → 目标站）链路更长，给更大超时；直连保持 25s
    timeout = kwargs.pop("timeout", 45 if os.getenv("PROXY_BASE", "").strip() and "?url=" in url else 25)
    for attempt in range(retries):
        try:
            host = urllib.parse.urlsplit(url).netloc.lower()
            with _REQUEST_LOCK:
                wait = MIN_REQUEST_INTERVAL - (time.monotonic() - _LAST_REQUEST_BY_HOST.get(host, 0))
                if wait > 0:
                    time.sleep(wait)
                _LAST_REQUEST_BY_HOST[host] = time.monotonic()
            response = requests.get(url, timeout=timeout, headers=headers, **kwargs)
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

def post_to_data(endpoint, data, retries=3):
    if not DATA_API_URL or not DATA_SYNC_SECRET:
        return None
    url = f"{DATA_API_URL}{endpoint}"
    for attempt in range(retries):
        try:
            response = requests.post(url, json=data, headers={"x-cron-secret": DATA_SYNC_SECRET}, timeout=45)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"DATA API sync failed {url}: {exc}") from exc
            time.sleep(2 ** attempt)

def get_site(endpoint):
    response = safe_get(f"{SITE_URL}{endpoint}")
    return response.json() if response else {"records": []}
