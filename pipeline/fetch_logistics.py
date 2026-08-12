import re
from utils import log, median, post_to_site, safe_get, today_str

SOURCES = ["http://jianghuawuliu.com/news/show-64.html", "https://zhengzhou.11467.com/info/53538230.htm"]
ROUTES = {"KZ":"阿拉木图", "UZ":"塔什干", "KG":"比什凯克", "TJ":"杜尚别"}
PATTERN = re.compile(r"(\d+)\s*[-–至]\s*(\d+)\s*天")

def _transit_days(text, city):
    """优先匹配 '至{城市}N-M天' 的精确时效；否则退回城市位置附近第一个 N-M 天。"""
    m = re.search(r"至" + re.escape(city) + r"\s*(\d+)\s*[-–至]\s*(\d+)\s*天", text)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2, m.group(0)
    pos = text.find(city)
    window = text[max(0, pos - 300):pos + 800] if pos >= 0 else text
    m = PATTERN.search(window)
    return ((int(m.group(1)) + int(m.group(2))) / 2, m.group(0)) if m else (None, None)

def run():
    # jianghuawuliu / 56zj 证书自签导致 verify 失败，单独关闭校验；11467 有 429 限流，靠重试退避
    pages = []
    for url in SOURCES:
        kwargs = {"verify": False} if ("jianghuawuliu" in url or "56zj" in url) else {}
        pages.append((url, safe_get(url, **kwargs)))
    for country, city in ROUTES.items():
        samples, used = [], []
        for url, response in pages:
            if not response: continue
            text = response.text
            days, matched = _transit_days(text, city)
            if days:
                samples.append(days); used.append(url)
        if not samples: log(f"logistics gap {city}"); continue
        post_to_site("/api/ingest/snapshot", {"metric":"logistics","country":country,"source":"物流公司官网","data":{"route":f"喀什/霍尔果斯—{city}","median_days":median(samples),"sample_count":len(samples),"observed_at":today_str(),"source_urls":used,"status":"live"}})
if __name__ == "__main__": run()
