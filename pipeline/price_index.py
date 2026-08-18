"""B1 跨五国食用菌价格指数模块。

数据源:站点公开读取接口 /api/prices(逐商品价格,含归一化 USD/kg)。
口径约束(与数据质量原则一致):
  - 仅采用 validationStatus == "valid" 且 normalizedPricePerKg 非空的记录
    (每公斤 USD 口径,不混入每包装价;needs_review 不进指数)
  - 聚合用中位数(抗离群值),不用均值
  - 五国价格指数以 KZ 为基准国(=100),其余国家相对值
  - 指数名称明确标注"零售价格指数",不冒充批发价

用法:
  python pipeline/price_index.py                 # 拉今日+近7/30天数据出报告
  python pipeline/price_index.py --days 30       # 自定义窗口
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta

from utils import safe_get

SITE_URL = "https://yinheng.site"
BASE_COUNTRY = "KZ"  # 基准国
COUNTRY_NAMES = {
    "KZ": "哈萨克斯坦", "UZ": "乌兹别克斯坦", "KG": "吉尔吉斯斯坦",
    "TJ": "塔吉克斯坦", "TM": "土库曼斯坦",
}
SPECIES_NAMES = {
    "button_mushroom": "双孢菇", "oyster_mushroom": "平菇", "shiitake": "香菇",
    "enoki": "金针菇", "king_oyster_mushroom": "杏鲍菇", "mixed_mushrooms": "混合菌类",
    "honey_fungus": "蜜环菌", "porcini": "牛肝菌", "shimeji": "真姬菇",
    "suillus": "乳牛肝菌", "chanterelle": "鸡油菌", "morel": "羊肚菌",
    "wood_ear": "木耳", "snow_fungus": "银耳", "straw_mushroom": "草菇",
    "truffle": "松露", "matsutake": "松茸",
}


def fetch_prices(date_str=None, limit=2000):
    """拉取价格记录;date_str 可选(Y-M-D),返回 (price, product) 对列表。"""
    url = f"{SITE_URL}/api/prices?limit={limit}"
    if date_str:
        url += f"&date={date_str}"
    r = safe_get(url, retries=2, timeout=30)
    if not r:
        return []
    return r.json().get("records", [])


def _valid_entries(records):
    """过滤有效且每公斤口径可比的记录,返回 [(country, species, usd_per_kg)]。

    换算:USD/kg = normalizedPricePerKg(本地货币/公斤) ÷ usdRateLocalPerUsd。
    接口无 normalizedPriceUsdPerKg 字段,需要现场换算;汇率缺失/非法则跳过。
    """
    out = []
    for rec in records:
        price, product = rec.get("price", {}), rec.get("product", {})
        if price.get("validationStatus") != "valid":
            continue
        local_kg = price.get("normalizedPricePerKg")
        rate = price.get("usdRateLocalPerUsd")
        if local_kg is None or local_kg <= 0 or not rate or float(rate) <= 0:
            continue  # 无每公斤口径或汇率,不进指数(不降证据要求)
        usd_kg = float(local_kg) / float(rate)
        country = product.get("country", "")
        species = product.get("speciesId", "")
        if country in COUNTRY_NAMES and species:
            out.append((country, species, usd_kg))
    return out


def compute_index(entries, base=BASE_COUNTRY):
    """按 国×菌种 聚合中位价,并计算五国指数(基准国=100)。"""
    by_key = defaultdict(list)
    for country, species, usd_kg in entries:
        by_key[(country, species)].append(usd_kg)
    # 菌种级:每国每菌种中位价
    median = {k: statistics.median(v) for k, v in by_key.items()}
    # 国家级:该国有数据的菌种中位价再取中位(国家综合指数)
    country_medians = defaultdict(list)
    for (country, _), m in median.items():
        country_medians[country].append(m)
    country_index = {c: statistics.median(v) for c, v in country_medians.items()}
    # 覆盖菌种数(供报告注明,避免跨菌种比较误读)
    coverage = {c: len({s for (cc, s) in by_key if cc == c}) for c in country_medians}
    # 指数化
    base_val = country_index.get(base)
    index = {}
    if base_val:
        index = {c: round(v / base_val * 100, 1) for c, v in country_index.items()}
    return {"median_by_species": median, "country_median": country_index,
            "index": index, "base_country": base, "coverage": coverage}


def render_markdown(result, label):
    lines = [f"## 五国食用菌零售价格指数({label})",
             "",
             f"基准国: {COUNTRY_NAMES.get(result['base_country'], result['base_country'])} = 100 | 口径: 有效报价每公斤 USD 中位价",
             "",
             "| 国家 | 综合中位价(USD/kg) | 指数 | 覆盖菌种数 |",
             "|---|---|---|---|"]
    for c in ("KZ", "UZ", "KG", "TJ", "TM"):
        if c in result["country_median"]:
            idx = result["index"].get(c, "-") if result["index"] else "-"
            cov = result.get("coverage", {}).get(c, "-")
            lines.append(f"| {COUNTRY_NAMES[c]} | {result['country_median'][c]:.2f} | {idx} | {cov} |")
    lines += ["",
              "> 注:综合指数=该国覆盖菌种中位价的再中位;覆盖菌种数不同时,",
              "> 跨国家合计数仅作参考,应以下方「菌种 × 国家」明细为准。"]
    # 菌种明细
    lines += ["", "### 菌种 × 国家 中位价(USD/kg)", "", "| 菌种 | " + " | ".join(COUNTRY_NAMES[c] for c in ("KZ", "UZ", "KG", "TJ", "TM")) + " |",
              "|---|" + "---|" * 5]
    species_order = sorted({s for (_, s) in result["median_by_species"]})
    for sp in species_order:
        cells = []
        for c in ("KZ", "UZ", "KG", "TJ", "TM"):
            m = result["median_by_species"].get((c, sp))
            cells.append(f"{m:.2f}" if m else "-")
        lines.append(f"| {SPECIES_NAMES.get(sp, sp)} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_report(days=30, date_str=None):
    """拉取窗口内数据,输出 (markdown, json, stats)。"""
    today = date.today()
    entries_by_day = {}
    # 拉近 days 天(每天一次,按 observationDate 过滤,避免跨日混入)
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        recs = fetch_prices(date_str=d)
        entries = _valid_entries(recs)
        if entries:
            entries_by_day[d] = entries
    if not entries_by_day:
        return None, None, {"error": "窗口内无有效价格数据"}
    # 当前指数 = 最近有数据的一天
    latest_day = max(entries_by_day)
    latest = compute_index(entries_by_day[latest_day])
    # 周变化:近 7 天 vs 之前(如果有)
    all_entries = [e for es in entries_by_day.values() for e in es]
    md = render_markdown(latest, f"{latest_day}")
    stats = {"days": len(entries_by_day), "latest_day": latest_day,
             "valid_entries": len(all_entries), "countries": sorted({e[0] for e in all_entries})}
    return md, {"latest": latest, "by_day": entries_by_day}, stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--date", type=str, default=None)
    args = ap.parse_args()
    md, data, stats = build_report(args.days, args.date)
    if md:
        print(md)
        print(f"\n<!-- stats: {json.dumps(stats, ensure_ascii=False)} -->")
        sys.stdout.flush()
    else:
        print("无有效价格数据:", stats)
