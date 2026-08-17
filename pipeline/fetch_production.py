"""采集 FAOSTAT 蘑菇与松露产量；估算值按官方 Flag 原样标注。"""
import datetime as dt
import os

from utils import log, post_to_site, safe_get


COUNTRIES = {"KZ": 108, "UZ": 235, "KG": 113, "TJ": 208, "TM": 213}
API = "https://fenixservices.fao.org/faostat/api/v1/en/data/QCL"


def run():
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    wanted_country = os.getenv("COUNTRY", "").strip().upper()
    for country, area_code in COUNTRIES.items():
        if wanted_country and country != wanted_country:
            continue
        response = safe_get(API, params={"area_code": area_code, "item_code": 449,
                                         "page_size": 1000}, retries=2, backoff=3, timeout=15)
        if not response:
            if not dry_run:
                post_to_site("/api/ingest/snapshot", {"metric": "production", "country": country,
                    "source": "FAOSTAT", "data": {"status": "gap", "reason": "unreachable",
                    "observed_at": dt.date.today().isoformat()}})
            continue
        try:
            payload = response.json()
            records = payload.get("data") or payload.get("Data") or []
        except (ValueError, AttributeError):
            records = []
        accepted = 0
        for row in records:
            year = row.get("Year") or row.get("year")
            value = row.get("Value") if "Value" in row else row.get("value")
            if year is None or value is None:
                continue
            flag = str(row.get("Flag") or row.get("flag") or "").strip()
            if not dry_run:
                post_to_site("/api/ingest/snapshot", {"metric": "production", "country": country,
                    "source": "FAOSTAT", "data": {"status": "live", "item": "Mushrooms and truffles",
                    "item_code": 449, "year": int(year), "value_tonnes": float(value),
                    "flag": flag, "is_estimate": flag.upper() == "I",
                    "source_url": API, "observed_at": dt.date.today().isoformat()}})
            accepted += 1
        if not accepted:
            if not dry_run:
                post_to_site("/api/ingest/snapshot", {"metric": "production", "country": country,
                    "source": "FAOSTAT", "data": {"status": "gap", "reason": "no_records",
                    "observed_at": dt.date.today().isoformat()}})
        log(f"FAOSTAT {country}: {accepted} 条")


if __name__ == "__main__":
    run()
