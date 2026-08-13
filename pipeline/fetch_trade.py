import datetime as dt
import time
from config import COUNTRIES, HS_CODES, UN_COMTRADE_API_KEY
from utils import log, post_to_site, safe_get

# 历史回溯窗口：UN Comtrade 提供 2018 至今的年度数据，
# 用于构建"年度进口单价"历史序列（value_usd / net_weight_kg = USD/kg）。
TRADE_YEARS = range(2018, dt.date.today().year + 1)


def _fetch(url, headers):
    response = safe_get(url, headers=headers, retries=1)
    return response.json().get("data", []) if response else []


def _unit_price(row):
    try:
        val = float(row.get("primaryValue") or 0)
        wgt = float(row.get("netWgt") or 0)
    except (TypeError, ValueError):
        return None
    return round(val / wgt, 2) if wgt > 0 else None


def run():
    for country, cfg in COUNTRIES.items():
        for hs in HS_CODES:
            for year in TRADE_YEARS:
                url = f"https://comtradeapi.un.org/data/v1/get/C/A/HS?period={year}&reporterCode={cfg['reporter']}&flowCode=M&partnerCode=0&cmdCode={hs}&partner2Code=0&customsCode=C00&motCode=0&maxRecords=50"
                headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if UN_COMTRADE_API_KEY else {}
                rows = _fetch(url, headers)
                if not rows:
                    log(f"trade gap {country} {hs} {year}")
                    time.sleep(1.5)
                    continue
                row = rows[0]
                unit = _unit_price(row)
                post_to_site("/api/ingest/snapshot", {"metric": "trade", "country": country, "source": "UN Comtrade",
                                                      "data": {"hs": hs, "year": year, "value_usd": row.get("primaryValue"),
                                                               "net_weight_kg": row.get("netWgt"),
                                                               "unit_price_usd_kg": unit,
                                                               "status": "live" if unit is not None else "gap"}})
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
