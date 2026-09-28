"""Deterministic, customer-facing daily report release from qualified observations."""

import math
import re
import unicodedata
from collections import defaultdict
from datetime import date

from sanity import check_usd_per_kg


COUNTRIES = {"LA": "老挝", "VN": "越南", "TH": "泰国", "MM": "缅甸", "KH": "柬埔寨", "KZ": "哈萨克斯坦", "UZ": "乌兹别克斯坦", "KG": "吉尔吉斯斯坦", "TJ": "塔吉克斯坦", "TM": "土库曼斯坦"}
SPECIES = {"oyster_mushroom": "平菇", "shiitake": "香菇", "wood_ear": "木耳", "king_oyster_mushroom": "杏鲍菇", "enoki": "金针菇", "button_mushroom": "双孢菇", "shimeji": "真姬菇", "porcini": "牛肝菌", "suillus": "乳牛肝菌", "honey_fungus": "蜜环菌", "snow_fungus": "银耳", "straw_mushroom": "草菇", "morel": "羊肚菌", "chanterelle": "鸡油菌"}
FORMS = {"fresh": "鲜品", "chilled": "冷藏鲜品", "dried": "干品", "frozen": "冷冻", "pickled": "腌渍", "canned": "罐装"}
WEIGHT = re.compile(r"(\d+(?:\.\d+)?)\s*(kg|g|克|千克|公斤)(?![a-z])", re.I)
PREPARED = re.compile(r"\b(?:porridge|soup|seasoning|sauce|meatballs?|noodles?|yogurt|pork|chicken|sausage|chao|mi an lien|hat nem|nuoc tuong|moc vien)\b|蘑菇粥|香菇粥|肉丸|调味料|方便面", re.I)
DRIED = re.compile(r"\b(?:dried|dry|kho|сушен\w*|сушён\w*)\b|干香菇|干木耳|干蘑菇", re.I)
PRESERVED = re.compile(r"\b(?:pickled|canned|marinated|маринован\w*)\b|罐头|腌渍", re.I)


def _number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result > 0 else None


def _ascii(value):
    return "".join(c for c in unicodedata.normalize("NFD", str(value or "")) if unicodedata.category(c) != "Mn").lower()


def _weight_kg(display):
    match = WEIGHT.fullmatch(str(display or "").strip())
    if not match:
        return None
    value = _number(match.group(1))
    return value / 1000 if value and match.group(2).lower() in {"g", "克"} else value


def _clean(value):
    return str(value or "").replace("|", "/").replace("\n", " ").strip()


def _channel(row):
    text = _clean(row["data"].get("platform_name") or row.get("source"))
    return re.sub(r"[（(][^）)]*(?:锚|待核|复核|采集)[^）)]*[）)]", "", text).strip()


def customer_price_is_eligible(row, today):
    """Admission affects only the report, never the original intelligence pool."""
    data = row.get("data", {})
    if row.get("country") not in COUNTRIES or data.get("observed_at") != today:
        return False
    if data.get("status") != "live" or data.get("validation_status") != "valid" or data.get("cross_validation_status") != "verified":
        return False
    if data.get("sanity_outlier") or data.get("sanity_outlier_original") or data.get("species_id") not in SPECIES:
        return False
    if data.get("product_form") not in FORMS or data.get("package_source") not in {"page_title", "page_structured_data"}:
        return False
    kg = _weight_kg(data.get("package_display"))
    price = _number(data.get("normalized_price_usd_per_kg"))
    if kg is None or price is None or _number(data.get("price_local")) is None or not data.get("currency"):
        return False
    if check_usd_per_kg(data["species_id"], row["country"], price)["sanity_outlier"]:
        return False
    if not _channel(row) or not re.match(r"https?://", str(data.get("source_url") or row.get("source_url") or "")):
        return False
    title = _ascii(data.get("original_title"))
    if not title or PREPARED.search(title):
        return False
    if data["product_form"] in {"fresh", "chilled"} and (DRIED.search(title) or PRESERVED.search(title)):
        return False
    title_weights = set()
    for match in WEIGHT.finditer(title):
        title_weights.add(float(match.group(1)) / (1000 if match.group(2).lower() in {"g", "克"} else 1))
    if len(title_weights) == 1 and not math.isclose(kg, next(iter(title_weights)), rel_tol=.005):
        return False
    usd = _number(data.get("price_usd"))
    if usd is not None and not math.isclose(usd / kg, price, rel_tol=.02, abs_tol=.02):
        return False
    return True


def select_customer_prices(rows, today, limit=20):
    date.fromisoformat(today)
    unique = {}
    for row in rows:
        if not customer_price_is_eligible(row, today):
            continue
        data = row["data"]
        key = (row["country"], data.get("product_key") or (data["species_id"], _channel(row), data.get("original_title")), data["package_display"], data["price_local"], data["currency"])
        unique.setdefault(key, row)
    buckets = defaultdict(list)
    for row in unique.values():
        buckets[row["country"]].append(row)
    for bucket in buckets.values():
        bucket.sort(key=lambda row: (list(SPECIES).index(row["data"]["species_id"]), row["data"]["product_form"], _channel(row), float(row["data"]["normalized_price_usd_per_kg"])))
        first = bucket[0]
        remainder = sorted(bucket[1:], key=lambda row: (row["data"]["species_id"] == first["data"]["species_id"], _channel(row) == _channel(first)))
        bucket[:] = [first, *remainder[:1]]
    selected = []
    # Round-robin gives each country a place before additional channel quotes.
    while buckets and len(selected) < min(limit, 20):
        for country in COUNTRIES:
            bucket = buckets.get(country)
            if not bucket:
                continue
            selected.append(bucket.pop(0))
            if not bucket:
                del buckets[country]
            if len(selected) >= min(limit, 20):
                break
    return selected


def _description(row):
    data = row["data"]
    return f'{COUNTRIES[row["country"]]}{_channel(row)}的{SPECIES[data["species_id"]]}（{FORMS[data["product_form"]]}，{_clean(data["package_display"])}装）'


def _quote(row):
    return f'{_description(row)}为{float(row["data"]["normalized_price_usd_per_kg"]):.2f}美元/公斤'


def _title(today, rows, recent_titles):
    day = date.fromisoformat(today)
    prefix = f"食用菌出海市场日报｜{day.month}月{day.day}日："
    candidates = []
    for row in rows:
        data = row["data"]
        for core in (f'{SPECIES[data["species_id"]]}{float(data["normalized_price_usd_per_kg"]):.2f}美元', f'{SPECIES[data["species_id"]]}报价更新'):
            if len((prefix + core).encode("utf-8")) <= 64:
                candidates.append(core)
    previous = str((recent_titles or [""])[0])
    core = next((candidate for candidate in candidates if candidate not in previous), candidates[0] if candidates else "价格更新")
    return prefix + core


def build_customer_report(today, rows, recent_titles=None, official_events=None):
    prices = select_customer_prices(rows, today)
    if not prices:
        raise ValueError(f"{today} has no report-ready price observations")
    # The first quotations anchor the decisions; remaining prices appear in tables.
    editorial = prices[:8]
    def item(index):
        return editorial[index % len(editorial)]
    points = [
        f'1. **{_quote(item(0))}。**建议按该包装先询批量采购价。',
        f'2. **{_quote(item(1))}。**建议向该渠道确认交货周期后再安排试单。',
        f'3. **{_quote(item(2))}。**建议销售报价同步写明形态和净重。',
    ]
    table_rows = prices[8:] if len(prices) > 8 else prices
    tables = []
    for form, label in FORMS.items():
        group = [row for row in table_rows if row["data"]["product_form"] == form]
        if not group:
            continue
        weights = [_weight_kg(row["data"]["package_display"]) * 1000 for row in group]
        size = f'{min(weights):g}g' if min(weights) == max(weights) else f'{min(weights):g}—{max(weights):g}g'
        lines = [f"### {label}", "", f"本组包装净重为{size}，建议按表列规格分别询价。", "", "| 国家 | 品类与规格 | 渠道 | 当地挂牌价 | 美元/公斤 | 观察日期 |", "|---|---|---|---:|---:|---|"]
        for row in group:
            data = row["data"]
            lines.append(f'| {COUNTRIES[row["country"]]} | {SPECIES[data["species_id"]]} {_clean(data["package_display"])}装 | {_channel(row)} | {_clean(data["price_local"])} {_clean(data["currency"])} | {float(data["normalized_price_usd_per_kg"]):.2f} | {today} |')
        tables.append("\n".join(lines))
    events = []
    for event in official_events or []:
        if not event.get("primarySource") or event.get("kind") not in {"policy", "news"}:
            continue
        if str(event.get("publishedAt", ""))[:10] != today or not all(event.get(field) for field in ("publisher", "title", "sourceUrl")):
            continue
        events.append(event)
        if len(events) == 5:
            break
    event_text = "\n\n".join(f'{_clean(event["publisher"])}于{today}发布《{_clean(event["title"])}》[S{index + 1}]。' for index, event in enumerate(events)) if events else "今日无新增政策与事件，市场面平稳。"
    body = "\n\n".join([
        "## 今日要点",
        "\n".join(points),
        "## 市场动态",
        event_text,
        "\n\n".join(tables),
        "## 机会与风险",
        f'- **询价机会：**{_quote(item(3))}。建议索取同规格整箱报价，起订量与周转计划匹配后再试单。',
        f'- **损耗风险：**{_quote(item(4))}。若到货包装或保存条件与询价要求不同，可能增加损耗；建议订单写明验收规格和保存条件。',
        "## 行动建议",
        f'- **决策参考：**{_quote(item(5))}；建议先计入运费、税费与损耗，再判断是否进入该渠道。',
        f'- **采购落地：**{_quote(item(6))}；建议向该渠道确认整箱数量、库存与交期，再确定首单数量。',
        f'- **报价规范：**{_quote(item(7))}；建议报价单同时列明原币价格、包装净重、交货地点和付款条件。',
        "## 数据说明",
        f"数据说明：本报告价格来自中亚及东南亚目标市场主流零售与电商渠道公开挂牌价，统一折算为美元/公斤。零售挂牌价与批发成交价、到岸成本存在差异，正式决策请以批量报价为准。数据来源：因恒科技监测，采集日期 {today}。如需核验具体报价来源，可联系专属客服索取。",
    ])
    if events:
        body += "\n\n来源：\n" + "\n".join(f'- [S{index + 1}] {_clean(event["publisher"])}｜{_clean(event["title"])}｜{today}' for index, event in enumerate(events))
    report = {"title": _title(today, prices, recent_titles), "body": body, "summary": f'{_quote(prices[0])}，建议按该包装先询批量采购价。', "prices": prices, "sources": [{"evidence_id": f"S{index + 1}", "document_id": event.get("id"), "source_type": event["kind"], "publisher": event["publisher"], "title": event["title"], "url": event["sourceUrl"], "published_at": today} for index, event in enumerate(events)]}
    validate_customer_report(report, today)
    return report


def validate_customer_report(report, today):
    body = report["body"]
    prices = report["prices"]
    headings = re.findall(r"^## (.+)$", body, re.M)
    if headings != ["今日要点", "市场动态", "机会与风险", "行动建议", "数据说明"]:
        raise ValueError("Daily report requires exactly five customer sections")
    if len(report["title"].encode("utf-8")) > 64:
        raise ValueError("Daily report title exceeds 64 UTF-8 bytes")
    if not 1 <= len(prices) <= 20 or not all(customer_price_is_eligible(row, today) for row in prices):
        raise ValueError("Daily report contains inadmissible price observations")
    if any(COUNTRIES[row["country"]] not in body for row in prices):
        raise ValueError("Daily report omitted an included country")
    points = body.split("## 市场动态", 1)[0]
    if not 3 <= len(re.findall(r"^\d+\. ", points, re.M)) <= 5:
        raise ValueError("Daily report requires three to five takeaways")
    forbidden = r"样本|报价有限|数据有限|仅作参考|仅供参考|自动复核|经核验|已核验|检索到|有效报价|有效观察|不作外推|不据此判断整体涨跌|不直接推导批发利润|本报告暂不|待进一步确认|原因待确认|待确认表|详见正文|详见上表|置信度|口径|中位价|周环比|https?://"
    if re.search(forbidden, body):
        raise ValueError("Daily report contains internal or unqualified language")
    source_prices = {f'{float(row["data"]["normalized_price_usd_per_kg"]):.2f}' for row in prices}
    quoted = set(re.findall(r"(\d+\.\d+)美元/公斤", body))
    quoted.update(re.findall(r"(\d+\.\d+)美元", report["title"]))
    for line in body.splitlines():
        if line.startswith("| ") and not line.startswith("| 国家"):
            fields = [part.strip() for part in line.strip("|").split("|")]
            if len(fields) in {5, 6}:
                quoted.add(fields[4])
                if len(fields) == 6 and fields[5] != today:
                    raise ValueError("Daily report table has a different observation date")
    if not quoted <= source_prices:
        raise ValueError("Daily report contains an unsupported price")
    if len(report.get("sources", [])) > 5:
        raise ValueError("Daily report has too many official sources")
    if len(body) > 3400:
        raise ValueError("Daily report exceeds the short-reading format")
    return True
