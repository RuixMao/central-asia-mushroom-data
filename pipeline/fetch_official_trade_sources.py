import datetime as dt
import hashlib

from config import UN_COMTRADE_API_KEY
from utils import log, post_to_site, safe_get


SOURCES = (
    {"id": "cn_customs", "countries": ("KZ", "UZ", "KG", "TJ", "TM"),
     "name": "中国海关统计", "url": "https://english.customs.gov.cn/Statistics/Statistics",
     "probe_url": "https://online.customs.gov.cn/ocportal/mySearch/",
     "role": "china_export_control", "scope": "国别及总体进出口校验；菌类双边值使用中国报告的 UN Comtrade 出口镜像"},
    {"id": "tj_statistics", "countries": ("TJ",), "name": "塔吉克斯坦国家统计局",
     "url": "https://www.stat.tj/ru/", "role": "importer_official_control",
     "scope": "国家进口总额与官方发布日历校验；暂无稳定公开 HS×伙伴国接口"},
    {"id": "tj_open_data", "countries": ("TJ",), "name": "塔吉克斯坦官方数据门户",
     "url": "https://data.stat.tj/", "role": "importer_official_control",
     "scope": "开放数据与宏观贸易指标校验"},
    {"id": "tm_statistics", "countries": ("TM",), "name": "土库曼斯坦国家统计委员会",
     "url": "https://stat.gov.tm/en", "role": "importer_official_control",
     "scope": "官方统计发布与分类器校验；暂无稳定公开 HS×伙伴国接口"},
    {"id": "tm_customs", "countries": ("TM",), "name": "土库曼斯坦海关",
     "url": "https://www.customs.gov.tm/", "role": "customs_official_control",
     "scope": "海关机构证据源；暂无稳定公开商品贸易下载接口"},
    {"id": "un_mirror_ru", "countries": ("KZ", "UZ", "KG", "TJ", "TM"),
     "name": "俄罗斯出口镜像", "url": "https://comtradeapi.un.org/", "role": "partner_export_mirror", "scope": "UN Comtrade 俄罗斯报告出口"},
    {"id": "un_mirror_kz", "countries": ("UZ", "KG", "TJ", "TM"),
     "name": "哈萨克斯坦出口镜像", "url": "https://comtradeapi.un.org/", "role": "partner_export_mirror", "scope": "UN Comtrade 哈萨克斯坦报告出口"},
    {"id": "un_mirror_tr", "countries": ("KZ", "UZ", "KG", "TJ", "TM"),
     "name": "土耳其出口镜像", "url": "https://comtradeapi.un.org/", "role": "partner_export_mirror", "scope": "UN Comtrade 土耳其报告出口"},
)


def run():
    checked_at = dt.datetime.now(dt.timezone.utc).isoformat()
    for source in SOURCES:
        headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if source["id"].startswith("un_mirror_") and UN_COMTRADE_API_KEY else {}
        probe_url = source.get("probe_url", source["url"])
        if source["id"].startswith("un_mirror_"):
            reporter = {"un_mirror_ru": 643, "un_mirror_kz": 398, "un_mirror_tr": 792}[source["id"]]
            partner = 860 if reporter == 398 else 398
            probe_url = ("https://comtradeapi.un.org/data/v1/get/C/A/HS"
                         f"?period=2024&reporterCode={reporter}&flowCode=X&partnerCode={partner}"
                         "&cmdCode=070951&partner2Code=0&customsCode=C00&motCode=0&maxRecords=50")
        response = safe_get(probe_url, headers=headers, retries=3, backoff=3, timeout=45)
        body = response.content if response else b""
        available = bool(response and body)
        digest = hashlib.sha256(body).hexdigest() if body else None
        for country in source["countries"]:
            post_to_site("/api/ingest/snapshot", {
                "metric": "trade", "country": country, "source": source["name"],
                "data": {"partner_code": "SOURCE_REGISTRY", "source_id": source["id"],
                         "source_name": source["name"], "source_url": source["url"],
                         "source_role": source["role"], "evidence_scope": source["scope"],
                         "supports_hs_partner_api": source["id"].startswith("un_mirror_"),
                         "availability": "reachable" if available else "unreachable",
                         "content_sha256": digest, "checked_at": checked_at,
                         "status": "live" if available else "gap"}
            })
        log(f"official source {source['id']} {'reachable' if available else 'unreachable'}")


if __name__ == "__main__":
    run()
