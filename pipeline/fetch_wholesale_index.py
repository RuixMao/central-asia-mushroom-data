"""官方批发价格指数采集(各国统计署)。

权威来源,可对外承诺。目标:
  - UZ:api.siat.stat.uz SDMX(渠道已验证,指标编号待确认)
  - KZ:stat.gov.kz(可达,API 路径待确认)
  - KG/TJ/TM:统计署公开表(待探测)

原则:
  - 只写已验证来源;找不到指标 → 明确 gap,不编造指数
  - 指标确认后走 snapshot(metric=wholesale)入库
"""
import datetime as dt

from utils import log, post_to_site, safe_get, today_str

# 已验证可达的数据源(指标编号待人工确认后启用)
SOURCES = [
    {
        "country": "UZ",
        "name": "乌兹别克斯坦国家统计委员会",
        "url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_3088.json",
        "status": "trade_verified",  # 3088 已验证为贸易数据;批发价指标编号待确认
    },
    {
        "country": "KZ",
        "name": "哈萨克斯坦战略规划与改革署统计局",
        "url": "https://stat.gov.kz/",
        "status": "reachable_api_pending",  # 首页可达,数据 API 待确认
    },
]


def run():
    today = today_str()
    for source in SOURCES:
        response = safe_get(source["url"], retries=2, backoff=2, timeout=30)
        if not response:
            log(f"wholesale index gap {source['country']} {source['name']}: unreachable")
            continue
        # 指标未确认前只记录可达性,不写入数据(避免编造)
        post_to_site("/api/ingest/snapshot", {
            "metric": "wholesale", "country": source["country"], "source": source["name"],
            "data": {"status": "source_reachable", "indicator": "pending_confirmation",
                     "observed_at": today, "note": "指标编号待确认后启用"}})
    log(f"官方批发价格指数源巡检完成: {dt.datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    run()
