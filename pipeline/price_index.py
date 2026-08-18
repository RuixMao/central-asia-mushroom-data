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
MIN_SAMPLE_FOR_CHANGE = 3  # 环比最小样本数:不足则该国/菌种环比不显示(防小样本噪声)
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
    """按 国×菌种 聚合中位价,计算国家级综合指数与菌种级指数(基准国=100)。"""
    by_key = defaultdict(list)
    for country, species, usd_kg in entries:
        by_key[(country, species)].append(usd_kg)
    median = {k: statistics.median(v) for k, v in by_key.items()}
    # 样本数(环比门槛用:样本太少的中位数波动大,环比不显示)
    counts = {k: len(v) for k, v in by_key.items()}
    # 国家级综合指数:该国有数据的菌种中位价再取中位
    country_medians = defaultdict(list)
    for (country, _), m in median.items():
        country_medians[country].append(m)
    country_index = {c: statistics.median(v) for c, v in country_medians.items()}
    coverage = {c: len({s for (cc, s) in by_key if cc == c}) for c in country_medians}
    # 国家级指数化
    base_val = country_index.get(base)
    index = {c: round(v / base_val * 100, 1) for c, v in country_index.items()} if base_val else {}
    # 菌种级指数:每个菌种单独指数化(基准国该菌种价=100;基准国缺该菌种则用
    # 有数据的国家中位价最低者作参照,避免跨菌种混杂)
    species_index = {}
    for sp in {s for (_, s) in by_key}:
        sp_median = {c: median[(c, sp)] for (c, s) in median if s == sp}
        if base in sp_median:
            ref = sp_median[base]
        else:
            ref = min(sp_median.values())
        species_index[sp] = {c: round(v / ref * 100, 1) for c, v in sp_median.items()} if ref else {}
    return {"median_by_species": median, "country_median": country_index,
            "index": index, "species_index": species_index,
            "base_country": base, "coverage": coverage, "counts": counts}


def _pct_change(cur, prev):
    """环比涨幅(%)。prev 为空返回 None(不伪造)。"""
    if cur is None or prev is None or prev <= 0:
        return None
    return round((cur - prev) / prev * 100, 1)


def render_markdown(result, label, prev_result=None):
    """渲染指数报告。prev_result 为 7 天前同口径结果(用于周环比)。"""
    lines = [f"## 五国食用菌零售价格指数({label})",
             "",
             f"基准国: {COUNTRY_NAMES.get(result['base_country'], result['base_country'])} = 100 | 口径: 有效报价每公斤 USD 中位价",
             "",
             "| 国家 | 综合中位价(USD/kg) | 指数 | 周环比 | 覆盖菌种数 |",
             "|---|---|---|---|---|"]
    for c in ("KZ", "UZ", "KG", "TJ", "TM"):
        if c in result["country_median"]:
            idx = result["index"].get(c, "-") if result["index"] else "-"
            cov = result.get("coverage", {}).get(c, "-")
            cur = result["country_median"][c]
            prev = prev_result["country_median"].get(c) if prev_result else None
            # 国家级环比:该国当日有效样本总数需达门槛(否则不显示)
            cur_n = sum(v for (cc, s), v in result.get("counts", {}).items() if cc == c)
            prev_n = sum(v for (cc, s), v in prev_result.get("counts", {}).items() if cc == c) if prev_result else 0
            chg = _pct_change(cur, prev) if (cur_n >= MIN_SAMPLE_FOR_CHANGE and prev_n >= MIN_SAMPLE_FOR_CHANGE) else None
            chg_str = f"{chg:+.1f}%" if chg is not None else "-"
            lines.append(f"| {COUNTRY_NAMES[c]} | {cur:.2f} | {idx} | {chg_str} | {cov} |")
    if prev_result is not None:
        lines += ["", f"> 周环比基准: {prev_result.get('_day', '更早')} 有数据日(同口径中位价对比)。"]
    lines += ["",
              "> 注:综合指数=该国覆盖菌种中位价的再中位;覆盖菌种数不同时,",
              "> 跨国家合计数仅作参考,应以下方「菌种 × 国家」明细为准。"]
    # 菌种明细(含菌种级指数与周环比)
    lines += ["", "### 菌种 × 国家 中位价(USD/kg)与菌种指数",
              "", "| 菌种 | " + " | ".join(f"{COUNTRY_NAMES[c]}价/指数" for c in ("KZ", "UZ", "KG", "TJ", "TM")) + " |",
              "|---|" + "---|" * 5]
    species_order = sorted({s for (_, s) in result["median_by_species"]})
    for sp in species_order:
        cells = []
        for c in ("KZ", "UZ", "KG", "TJ", "TM"):
            m = result["median_by_species"].get((c, sp))
            if m:
                si = result.get("species_index", {}).get(sp, {}).get(c)
                cur = m
                prev = prev_result["median_by_species"].get((c, sp)) if prev_result else None
                cur_n = result.get("counts", {}).get((c, sp), 0)
                prev_n = prev_result.get("counts", {}).get((c, sp), 0) if prev_result else 0
                chg = _pct_change(cur, prev) if (cur_n >= MIN_SAMPLE_FOR_CHANGE and prev_n >= MIN_SAMPLE_FOR_CHANGE) else None
                parts = f"{m:.2f}"
                if si is not None:
                    parts += f"({si})"
                if chg is not None:
                    parts += f"{chg:+.1f}%"
                cells.append(parts)
            else:
                cells.append("-")
        lines.append(f"| {SPECIES_NAMES.get(sp, sp)} | " + " | ".join(cells) + " |")
    lines += ["",
              f"> 口径说明:①仅计入有效(valid)报价,每公斤 USD 中位价;②菌种指数以该菌种",
              f"> 哈萨克斯坦价=100(哈缺该菌种时以最低价国为参照);③周环比为同口径中位价",
              f"> 对比,单日样本 < {MIN_SAMPLE_FOR_CHANGE} 条不显示(防小样本噪声)。"]
    return "\n".join(lines)


def build_report(days=7, date_str=None, week_offset=7):
    """拉取窗口内数据,输出 (markdown, json, stats)。

    - 当前指数 = 窗口内最近有数据的一天
    - 周环比 = 对比 week_offset 天前(默认 7 天)同口径;不足则返回 None 不伪造
    - days 默认 7(数据只积累到近 7 天,拉 30 天徒增请求且无收益)
    """
    today = date.today()
    entries_by_day = {}
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        recs = fetch_prices(date_str=d)
        entries = _valid_entries(recs)
        if entries:
            entries_by_day[d] = entries
    if not entries_by_day:
        return None, None, {"error": "窗口内无有效价格数据"}
    latest_day = max(entries_by_day)
    latest = compute_index(entries_by_day[latest_day])
    latest["_day"] = latest_day
    # 环比基准:优先取 week_offset 天前;数据积累不足时退化为窗口内最早
    # 有数据的一天(诚实标注实际间隔,不伪造 7 天前)
    sorted_days = sorted(entries_by_day.keys())
    target = today - timedelta(days=week_offset)
    prev_day = None
    for d in reversed(sorted_days):
        if d < latest_day and d <= target.isoformat():
            prev_day = d
            break
    if prev_day is None and len(sorted_days) >= 2:
        prev_day = sorted_days[0]  # 窗口最早一天(不足 7 天时的退化基准)
    prev = compute_index(entries_by_day[prev_day]) if prev_day else None
    if prev is not None:
        prev["_day"] = prev_day
    md = render_markdown(latest, f"{latest_day}", prev_result=prev)
    all_entries = [e for es in entries_by_day.values() for e in es]
    stats = {"days": len(entries_by_day), "latest_day": latest_day,
             "prev_day": prev_day, "valid_entries": len(all_entries),
             "countries": sorted({e[0] for e in all_entries})}
    return md, {"latest": latest, "prev": prev, "by_day": entries_by_day}, stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--date", type=str, default=None)
    args = ap.parse_args()
    md, data, stats = build_report(args.days, args.date)
    if md:
        print(md)
        print(f"\n<!-- stats: {json.dumps(stats, ensure_ascii=False)} -->")
        sys.stdout.flush()
    else:
        print("无有效价格数据:", stats)
