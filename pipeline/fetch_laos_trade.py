"""Focused Lao PDR mushroom trade collector using low-volume Comtrade queries."""

import datetime as dt
import os
import time

from utils import log, post_to_site, safe_get


REPORTER = 418
HS_CODES = ("070951", "070959", "200310")
PARTNERS = (("CN", 156, "中国"), ("VN", 704, "越南"), ("TH", 764, "泰国"))
PREVIEW = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"


def _years():
    configured = [part.strip() for part in os.getenv("LAOS_TRADE_YEARS", "").split(",") if part.strip()]
    if configured:
        return tuple(int(year) for year in configured)
    current = dt.date.today().year
    return (current - 4, current - 3, current - 2, current - 1)


def _query(year, reporter, flow, partner):
    params = (f"?period={year}&reporterCode={reporter}&flowCode={flow}&partnerCode={partner}"
              f"&cmdCode={','.join(HS_CODES)}&partner2Code=0&customsCode=C00&motCode=0&maxRecords=500")
    response = safe_get(PREVIEW + params, retries=4, backoff=4, timeout=60)
    return response.json().get("data", []) if response else []


def _number(row, key):
    try:
        value = row.get(key)
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def normalize_rows(rows):
    normalized = []
    for row in rows:
        hs = str(row.get("cmdCode") or "")
        value = _number(row, "primaryValue")
        weight = _number(row, "netWgt")
        if hs not in HS_CODES or value is None:
            continue
        normalized.append({"hs": hs, "value_usd": value, "net_weight_kg": weight,
                           "unit_price_usd_kg": round(value / weight, 4) if weight and weight > 0 else None})
    return normalized


def collect(fetch=_query, years=None, pause=8):
    years = tuple(years or _years())
    records = []
    for year in years:
        importer = normalize_rows(fetch(year, REPORTER, "M", 0))
        for row in importer:
            records.append({**row, "year": year, "partner_code": "ALL", "partner_name": "全球",
                            "reporting_basis": "importer_official", "source": "UN Comtrade（老挝进口申报）"})
        if pause:
            time.sleep(pause)
        for partner_code, reporter, partner_name in PARTNERS:
            mirror = normalize_rows(fetch(year, reporter, "X", REPORTER))
            for row in mirror:
                records.append({**row, "year": year, "partner_code": partner_code, "partner_name": partner_name,
                                "reporting_basis": "exporter_mirror", "source": f"UN Comtrade（{partner_name}出口镜像）"})
            if pause:
                time.sleep(pause)
    return records


def market_summaries(records):
    summaries = []
    for year in sorted({row["year"] for row in records}):
        annual = [row for row in records if row["year"] == year]
        importer = [row for row in annual if row["reporting_basis"] == "importer_official"]
        mirrors = [row for row in annual if row["reporting_basis"] == "exporter_mirror"]
        if importer:
            summaries.append({"year": year, "market_size_usd": round(sum(row["value_usd"] for row in importer), 2),
                              "market_size_basis": "importer_official", "estimate_lower_usd": None,
                              "confirmed_quantity_kg": sum(row["net_weight_kg"] or 0 for row in importer),
                              "confirmed_partners": [], "status": "live"})
        elif mirrors:
            summaries.append({"year": year, "market_size_usd": None,
                              "market_size_basis": "partner_mirror_lower_bound",
                              "estimate_lower_usd": round(sum(row["value_usd"] for row in mirrors), 2),
                              "confirmed_quantity_kg": sum(row["net_weight_kg"] or 0 for row in mirrors),
                              "confirmed_partners": sorted({row["partner_name"] for row in mirrors}), "status": "live"})
    return summaries


def run():
    records = collect()
    for row in records:
        post_to_site("/api/ingest/snapshot", {"metric": "trade", "country": "LA", "source": row["source"],
                     "data": {**{key: value for key, value in row.items() if key != "source"}, "status": "live"}})
    for summary in market_summaries(records):
        post_to_site("/api/ingest/snapshot", {"metric": "trade", "country": "LA",
                     "source": "UN Comtrade 老挝菌类市场规模", "data": {**summary, "partner_code": "MARKET_SIZE"}})
    log(f"Laos trade records written: {len(records)}; market summaries: {len(market_summaries(records))}")


if __name__ == "__main__":
    run()
