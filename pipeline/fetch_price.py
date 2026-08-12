import re
import time
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from config import COUNTRIES, VARIETIES, FX_TO_CNY
from utils import log, post_to_site, safe_get, today_str

PRICE_RE = re.compile(r"(\d[\d\s,.]*)\s*(₸|сум|сомони|сом|TMT|KZT|UZS|KGS|TJS)", re.I)
SPEC_RE = re.compile(r"(\d+(?:[.,]\d+)?\s*(?:г|гр|kg|кг|ml|мл|箱|шт))", re.I)
DYNAMIC = {"arbuz", "uzum", "korzinka", "tegen", "tm_market"}

def generic_parser(html, base_url, variety, channel="电商"):
    soup = BeautifulSoup(html, "html.parser")
    keyword = VARIETIES[variety].get("ru", "").lower()
    records = []
    for node in soup.select("article, .product, .product-card, .item, .goods, li")[:120]:
        text = " ".join(node.get_text(" ", strip=True).split())
        if keyword and keyword not in text.lower() and variety not in text: continue
        price = PRICE_RE.search(text)
        if not price: continue
        value = float(price.group(1).replace(" ", "").replace(",", "."))
        spec = SPEC_RE.search(text)
        link = node.select_one("a[href]")
        records.append({"variety":variety,"form":"加工品" if any(x in text.lower() for x in ("марин", "суш", "консерв")) else "鲜品","spec":spec.group(1) if spec else "规格待核","channel":channel,"price_local":value,"source_url":urljoin(base_url, link.get("href")) if link else base_url,"status":"live"})
    return records[:20]

def parse_arbuz(h,u,v): return generic_parser(h,u,v,"生鲜电商")
def parse_carefood(h,u,v): return generic_parser(h,u,v,"批发")
def parse_flagma_kz(h,u,v): return generic_parser(h,u,v,"批发/分类信息")
def parse_uzum(h,u,v): return generic_parser(h,u,v,"综合电商")
def parse_korzinka(h,u,v): return generic_parser(h,u,v,"连锁商超")
def parse_olx_uz(h,u,v): return generic_parser(h,u,v,"分类信息")
def parse_tegen(h,u,v): return generic_parser(h,u,v,"食材批发")
def parse_globus(h,u,v): return generic_parser(h,u,v,"商超")
def parse_omarket(h,u,v): return generic_parser(h,u,v,"本地电商")
def parse_lalafo(h,u,v): return generic_parser(h,u,v,"分类信息")
def parse_zudbiyor(h,u,v): return generic_parser(h,u,v,"即时零售")
def parse_magnit(h,u,v): return generic_parser(h,u,v,"线上商超")
def parse_somon(h,u,v): return generic_parser(h,u,v,"分类信息")
def parse_tm_market(h,u,v): return generic_parser(h,u,v,"本地电商")
def parse_flagma_tm(h,u,v): return generic_parser(h,u,v,"批发/分类信息")
def parse_ashgabat_supplier(h,u,v): return generic_parser(h,u,v,"供应商")

PARSERS = {name: globals()[f"parse_{name}"] for cfg in COUNTRIES.values() for name,_ in cfg["platforms"]}

def amazon_is_local(record, country):
    cfg = COUNTRIES[country]
    return record.get("deliver_country") == country and record.get("currency") == cfg["currency"] and record.get("orderable") is True

def run():
    summary = []
    for country, cfg in COUNTRIES.items():
        for variety, words in VARIETIES.items():
            keyword = words.get(cfg["lang"], words["ru"])
            found = []
            for platform, template in cfg["platforms"]:
                url = template.format(q=quote(keyword))
                if platform in DYNAMIC: log(f"NEEDS_BROWSER {platform} {country} {variety}")
                response = safe_get(url)
                if response:
                    try: found.extend((platform, row) for row in PARSERS[platform](response.text, url, variety))
                    except Exception as exc: log(f"parser error {platform}: {exc}")
                time.sleep(1)
            if not found:
                reason = f"未在 {len(cfg['platforms'])} 个平台发现该品类"
                post_to_site("/api/ingest/snapshot", {"metric":"price_retail","country":country,"source":"weekly-price-crawler","data":{"variety":variety,"status":"gap","reason":reason,"observed_at":today_str()}})
                summary.append(f"{country} {variety}缺（{reason}）")
                continue
            for platform, row in found:
                row.update({"currency":cfg["currency"],"price_cny":round(row["price_local"]*FX_TO_CNY[cfg["currency"]],2),"observed_at":today_str()})
                post_to_site("/api/ingest/snapshot", {"metric":"price_retail","country":country,"source":platform,"data":row})
            values = [row["price_cny"] for _,row in found]
            summary.append(f"{country} {variety} ¥{min(values):.2f}–{max(values):.2f}（{len(found)}条）")
    log("本周采集摘要：" + "；".join(summary))
if __name__ == "__main__": run()
