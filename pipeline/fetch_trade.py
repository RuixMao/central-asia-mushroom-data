import datetime as dt
import time
from config import COUNTRIES, HS_CODES, UN_COMTRADE_API_KEY
from utils import log, post_to_site, safe_get

# 历史回溯窗口：UN Comtrade 提供 2018 至今的年度数据，
# 用于构建"年度进口单价"历史序列（value_usd / net_weight_kg = USD/kg）。
TRADE_YEARS = range(2018, dt.date.today().year + 1)
TRADE_PARTNERS = (("CN", 156), ("RU", 643), ("KZ", 398), ("BY", 112), ("TR", 792))


def _fetch(url, headers):
    response = safe_get(url, headers=headers, retries=4, backoff=3)
    return response.json().get("data", []) if response else []


def _unit_price(row):
    try:
        val = float(row.get("primaryValue") or 0)
        wgt = float(row.get("netWgt") or 0)
    except (TypeError, ValueError):
        return None
    return round(val / wgt, 2) if wgt > 0 else None


def _query(reporter, flow, partner, hs, year, headers):
    url = ("https://comtradeapi.un.org/data/v1/get/C/A/HS"
           f"?period={year}&reporterCode={reporter}&flowCode={flow}&partnerCode={partner}"
           f"&cmdCode={hs}&partner2Code=0&customsCode=C00&motCode=0&maxRecords=50")
    rows = _fetch(url, headers)
    return rows[0] if rows else {}


def _value(row):
    try:
        value = row.get("primaryValue")
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _post(country, hs, year, partner_code, row, basis, source):
    value = _value(row)
    unit = _unit_price(row) if row else None
    post_to_site("/api/ingest/snapshot", {
        "metric": "trade", "country": country, "source": source,
        "data": {"hs": hs, "year": year, "partner_code": partner_code,
                 "value_usd": value, "partner_value_usd": value,
                 "net_weight_kg": row.get("netWgt") if row else None,
                 "unit_price_usd_kg": unit, "partner_unit_price_usd_kg": unit,
                 "reporting_basis": basis, "status": "live" if value is not None else "gap"}
    })
    return value


def run():
    headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if UN_COMTRADE_API_KEY else {}
    for country, cfg in COUNTRIES.items():
        for hs in HS_CODES:
            for year in TRADE_YEARS:
                total_row = _query(cfg["reporter"], "M", 0, hs, year, headers)
                official_total = _post(country, hs, year, "ALL", total_row,
                                       "importer_official", "UN Comtrade（进口国申报）")
                effective_values = []
                live_sources = 0
                for partner_code, partner in TRADE_PARTNERS:
                    if partner == cfg["reporter"]:
                        continue
                    direct_row = _query(cfg["reporter"], "M", partner, hs, year, headers)
                    direct_value = _value(direct_row)
                    if direct_value is not None:
                        value = _post(country, hs, year, partner_code, direct_row,
                                      "importer_official", "UN Comtrade（进口国申报）")
                    else:
                        mirror_row = _query(partner, "X", cfg["reporter"], hs, year, headers)
                        mirror_source = "UN Comtrade（中国海关出口镜像）" if partner_code == "CN" else "UN Comtrade（伙伴国出口镜像）"
                        value = _post(country, hs, year, partner_code, mirror_row,
                                      "exporter_mirror", mirror_source)
                    if value is not None:
                        effective_values.append(value)
                        live_sources += 1
                    time.sleep(1.5)
                mirror_sum = sum(effective_values)
                source_count = len([p for p in TRADE_PARTNERS if p[1] != cfg["reporter"]])
                if official_total is not None:
                    lower = upper = official_total
                    coverage = min(100.0, mirror_sum / official_total * 100) if official_total > 0 else 100.0
                    confidence = "high" if coverage >= 80 else "medium" if coverage >= 40 else "low"
                    basis = "importer_official"
                elif mirror_sum > 0:
                    observed_ratio = live_sources / max(source_count, 1)
                    lower = mirror_sum
                    upper = mirror_sum / max(observed_ratio, 0.4)
                    coverage = observed_ratio * 100
                    confidence = "medium" if observed_ratio >= .8 else "low"
                    basis = "partner_mirror_estimate"
                else:
                    lower = upper = None
                    coverage = 0.0
                    confidence = "insufficient"
                    basis = "insufficient"
                post_to_site("/api/ingest/snapshot", {
                    "metric": "trade", "country": country, "source": "UN Comtrade 多源补位",
                    "data": {"hs": hs, "year": year, "partner_code": "ESTIMATE",
                             "estimate_lower_usd": lower, "estimate_upper_usd": upper,
                             "coverage_pct": round(coverage, 1), "confidence": confidence,
                             "reporting_basis": basis, "live_source_count": live_sources,
                             "status": "live" if lower is not None else "gap"}
                })
                log(f"trade estimate {country} {hs} {year} basis={basis} confidence={confidence}")
                time.sleep(1.5)
    # 月度数据（尽力而为）：UN Comtrade 部分国家/产品提供月度序列，
    # 采最近 24 个月，用作月度价格参考；接口不支持时自动跳过（不影响年度主链路）。
    try:
        for country, cfg in COUNTRIES.items():
            for hs in HS_CODES:
                url = f"https://comtradeapi.un.org/data/v1/get/C/M/HS?period=202401-202512&reporterCode={cfg['reporter']}&flowCode=M&partnerCode=0&cmdCode={hs}&partner2Code=0&customsCode=C00&motCode=0&maxRecords=500"
                headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if UN_COMTRADE_API_KEY else {}
                rows = _fetch(url, headers)
                if not rows:
                    log(f"trade monthly gap {country} {hs}")
                    time.sleep(1.5)
                    continue
                for row in rows:
                    period = row.get("period")
                    unit = _unit_price(row)
                    if not period or unit is None:
                        continue
                    post_to_site("/api/ingest/snapshot", {"metric": "trade", "country": country, "source": "UN Comtrade",
                                                          "data": {"hs": hs, "year": period[:4], "month": period[-2:],
                                                                   "value_usd": row.get("primaryValue"),
                                                                   "net_weight_kg": row.get("netWgt"),
                                                                   "unit_price_usd_kg": unit,
                                                                   "period_type": "monthly", "status": "live"}})
                time.sleep(1.5)
    except Exception as exc:
        log(f"trade monthly skipped: {exc}")


if __name__ == "__main__":
    run()
