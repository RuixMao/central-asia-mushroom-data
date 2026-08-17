"""Collect Uzbekistan's official monthly two-digit import benchmarks."""
import datetime as dt

from utils import log, post_to_site, safe_get

SOURCE_URL = "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_3088.json"
CHAPTERS = {"07": "食用蔬菜及根茎类", "20": "蔬菜、水果及植物制品"}


def extract_chapters(payload):
    blocks = payload if isinstance(payload, list) else [payload]
    rows = []
    for block in blocks:
        for row in block.get("data", []):
            code = str(row.get("Code", "")).zfill(2)
            if code not in CHAPTERS:
                continue
            periods = sorted(key for key in row if key[:4].isdigit() and "-M" in key)
            if not periods or row.get(periods[-1]) is None:
                continue
            period = periods[-1]
            rows.append({"chapter": code, "period": period, "value_usd": float(row[period]) * 1000,
                         "label_zh": CHAPTERS[code], "label_en": row.get("Klassifikator_en")})
    return rows


def run():
    response = safe_get(SOURCE_URL, retries=4, backoff=3, timeout=45)
    if not response:
        raise RuntimeError("Uzbekistan official statistics unavailable")
    rows = extract_chapters(response.json())
    if len(rows) != len(CHAPTERS):
        raise RuntimeError("Uzbekistan official chapter data incomplete")
    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    for row in rows:
        post_to_site("/api/ingest/snapshot", {"metric": "trade", "country": "UZ", "source": "乌兹别克斯坦国家统计委员会",
            "data": {**row, "reporting_basis": "importer_official_chapter_benchmark", "source_url": SOURCE_URL,
                     "retrieved_at": retrieved_at, "status": "live"}})
    log(f"Uzbekistan official trade benchmarks written: {len(rows)}")


if __name__ == "__main__":
    run()
