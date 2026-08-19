"""独立汇率日序列，为周报以上报告提供可比的汇率变化。"""

import datetime as dt

from config import COUNTRIES
from utils import log, post_to_site, safe_get, today_str

SOURCE_URL = "https://fxapi.app/api/usd.json"


def extract_rates(payload):
    rates = payload.get("rates") or {}
    cny = rates.get("CNY")
    if not cny:
        raise ValueError("CNY rate missing")
    rows = []
    for country, config in COUNTRIES.items():
        currency = config["currency"]
        local = rates.get(currency)
        if not local:
            continue
        rows.append({"country": country, "currency": currency, "local_per_usd": float(local),
                     "cny_per_usd": float(cny), "local_per_cny": round(float(local) / float(cny), 8)})
    return rows


def run():
    response = safe_get(SOURCE_URL, retries=3, backoff=2, timeout=30)
    if not response:
        raise RuntimeError("FX source unavailable")
    payload = response.json();rows = extract_rates(payload);today = today_str()
    if len(rows) != len(COUNTRIES):
        raise RuntimeError(f"FX coverage incomplete: {len(rows)}/{len(COUNTRIES)}")
    for row in rows:
        post_to_site("/api/ingest/snapshot", {"metric": "fx", "country": row["country"], "source": "fxapi.app",
            "data": {**{k:v for k,v in row.items() if k != "country"}, "base": "USD", "date": today,
                     "observed_at": today, "source_timestamp": payload.get("timestamp"), "status": "live"}})
    log(f"FX daily series written: {len(rows)} currencies at {dt.datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":run()
