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

def parse_price_text(raw):
    """千分位/小数点兼容价格解析(全适配器统一入口)。

    中亚站点价格习惯各异:45,000(千分位逗号)/45.00(小数点)/128,70(小数点逗号)/
    45 000(空格)/1,234.56(千分位+小数点)。统一规则:
      - 同时含 , 和 . → 逗号是千分位,去掉(1,234.56 -> 1234.56)
      - 仅含 , → 看小数部分:3 位且前面有数字当千分位(45,000 -> 45000),
        否则当小数点(128,70 -> 128.70)
      - 空格/窄空格直接去除
    解析失败返回 None(调用方按 gap 处理,不写 0)。
    """
    if raw is None:
        return None
    s = str(raw).replace(" ", "").replace("\u202f", "").replace("\u00a0", "").strip()
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) >= 3 or (len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) > 0):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def find_price_match(node, pattern):
    """只在单个 DOM 文本节点内匹配价格。

禁止先把整页/整卡片压成一行再匹配，否则轮播序号“1”和
价格“128,70”可能被拼成“1 128,70”。找不到时宁可返回 None，
不跨节点猜测。
    """
    strings = node.find_all(string=True) if hasattr(node, "find_all") else ()
    for value in strings:
        if getattr(value, "parent", None) is not None and value.parent.name in {"script", "style", "noscript"}:
            continue
        text = " ".join(str(value).split())
        for match in pattern.finditer(text):
            price = parse_price_text(match.group(1))
            if price is not None and price > 0:
                return match, price
    return None, None


def response_text(response):
    """按 UTF-8 解码响应体(全适配器统一入口)。

    中亚站点 header 常把 charset 错标为 latin-1/ISO-8859-1(实际是 UTF-8),
    requests 的 response.text 会按错误编码解码 → 本地语言字符变 mojibake
    (ö 变成 Ã¶)。强制 UTF-8 解码,失败时回退 requests 默认行为。
    兼容测试用 mock(无真实 .content bytes 时回退 .text)。
    """
    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            pass
    text = getattr(response, "text", "")
    return text if isinstance(text, str) else ""

# 数据中心出口 IP 被目标站防火墙/反爬拒绝的域名(本地直连正常、CI 必挂)。
# 设置环境变量 PROXY_BASE(如 https://tm-proxy.xxx.workers.dev)后,
# 这些域名的请求改经 CF Worker 中转出口;不设置则保持直连(本地正常)。
# gipertm/asmanexpress = TM 站防火墙;olx.uz = 数据中心 IP 反爬(2026-08 实测)
PROXY_DOMAINS = ("gipertm.com", "asmanexpress.com", "olx.uz")
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

def delete_from_site(endpoint, cron_secret=CRON_SECRET):
    response = requests.delete(f"{SITE_URL}{endpoint}", headers={"x-cron-secret": cron_secret}, timeout=30)
    response.raise_for_status()
    return response.json()

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
