"""官方市场平均价格采集(UZ SIAT 1308 等)。

来源核对(2026-08-18 人工核实):
  - SIAT 数据集 1308 | 统计代码 1.11.03.0001
  - 名称:「市场和商店中部分商品平均价格动态」(市场及商店平均价格)
  - ⚠️ 不是"批发价格",对外引用必须用准确名称,不得标注为批发价
  - 官方页面显示数据更新至 2026-08-11
  - 数据结构:41 行商品 × 2021 起月度均值(米/面等主粮,当前不含蘑菇)

命名约定:
  - 程序内用页面 ID 1308 引用
  - 对外/报告保存统计代码 1.11.03.0001
  - metric 用 market_avg_price(避免与批发 wholesale 混淆)

原则:
  - 只写已验证来源;找不到指标 → 明确 gap,不编造指数
  - 诚实标注口径,不把"市场平均价"冒充"批发价"
"""
import datetime as dt

from utils import log, post_to_site, safe_get, today_str

SOURCES = [
    {
        "country": "UZ",
        "name": "乌兹别克斯坦国家统计委员会",
        "url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_1308.json",
        "page_id": "1308",
        "stat_code": "1.11.03.0001",
        "indicator": "市场与商店平均价格动态",
        "verified": True,
        "verified_date": "2026-08-18",
        "note": "市场/商店平均价,非批发价;更新至 2026-08-11",
    },
    {
        "country": "KZ",
        "name": "哈萨克斯坦战略规划与改革署统计局",
        "url": "https://stat.gov.kz/",
        "page_id": None,
        "stat_code": None,
        "indicator": "待确认",
        "verified": False,
        "verified_date": None,
        "note": "首页可达,数据 API 待确认",
    },
]


def _latest_value(row, value_keys):
    """取最近一个有值的月份(如 2026-М07),返回 (period, value)。"""
    periods = sorted((k for k in value_keys if "-М" in k), reverse=True)
    for period in periods:
        value = row.get(period)
        if value is not None:
            return period, value
    return None, None


def run():
    today = today_str()
    for source in SOURCES:
        if not source["verified"]:
            log(f"market avg price gap {source['country']}: indicator pending ({source['note']})")
            continue
        response = safe_get(source["url"], retries=2, backoff=2, timeout=30)
        if not response:
            log(f"market avg price gap {source['country']}: unreachable")
            continue
        try:
            payload = response.json()
        except ValueError:
            log(f"market avg price gap {source['country']}: non-json response")
            continue
        blocks = payload if isinstance(payload, list) else [payload]
        rows = []
        for block in blocks:
            rows.extend(block.get("data", []))
        if not rows:
            log(f"market avg price gap {source['country']}: empty data")
            continue
        # 写入最新一期全量商品价格快照(诚实标注为市场平均价)
        value_keys = list(rows[0].keys())
        summary = []
        for row in rows[:40]:
            period, value = _latest_value(row, value_keys)
            if value is None:
                continue
            summary.append({
                "code": row.get("Code"),
                "name_uz": row.get("Klassifikator"),
                "name_ru": row.get("Klassifikator_ru"),
                "name_en": row.get("Klassifikator_en"),
                "period": period,
                "avg_price": value,
            })
        post_to_site("/api/ingest/snapshot", {
            "metric": "market_avg_price", "country": source["country"], "source": source["name"],
            "data": {
                "indicator": source["indicator"],
                "page_id": source["page_id"],
                "stat_code": source["stat_code"],
                "row_count": len(summary),
                "latest_period": summary[0]["period"] if summary else None,
                "items": summary,
                "observed_at": today,
                "note": source["note"],
            }})
        log(f"market avg price OK {source['country']}: {len(summary)} 商品, 最新期 {summary[0]['period'] if summary else 'N/A'}")
    log(f"官方市场平均价采集完成: {dt.datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    run()
