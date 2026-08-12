import datetime as dt
import statistics
import time
import requests
from config import SITE_URL, CRON_SECRET

def log(message): print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {message}", flush=True)
def today_str(): return dt.date.today().isoformat()
def median(nums): return statistics.median(nums) if nums else None

def safe_get(url, retries=3, backoff=2, **kwargs):
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
            return response.json()
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"POST failed {url}: {exc}") from exc
            time.sleep(2 ** attempt)

def get_site(endpoint):
    response = safe_get(f"{SITE_URL}{endpoint}")
    return response.json() if response else {"records": []}
