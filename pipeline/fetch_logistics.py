import re
from utils import log, median, post_to_site, safe_get, today_str

SOURCES = ["http://jianghuawuliu.com/news/show-64.html", "https://zhengzhou.11467.com/info/53538230.htm", "https://www.56zj.net/line/zhongya.html"]
ROUTES = {"KZ":"阿拉木图", "UZ":"塔什干", "KG":"比什凯克", "TJ":"杜尚别"}
PATTERN = re.compile(r"(\d+)\s*[-–至]\s*(\d+)\s*天")

def run():
    pages = [(url, safe_get(url)) for url in SOURCES]
    for country, city in ROUTES.items():
        samples, used = [], []
        for url, response in pages:
            if not response: continue
            text = response.text
            pos = text.find(city)
            match = PATTERN.search(text[max(0,pos-300):pos+800] if pos >= 0 else text)
            if match: samples.append((int(match.group(1))+int(match.group(2)))/2); used.append(url)
        if not samples: log(f"logistics gap {city}"); continue
        post_to_site("/api/ingest/snapshot", {"metric":"logistics","country":country,"source":"物流公司官网","data":{"route":f"喀什/霍尔果斯—{city}","median_days":median(samples),"sample_count":len(samples),"observed_at":today_str(),"source_urls":used,"status":"live"}})
if __name__ == "__main__": run()
