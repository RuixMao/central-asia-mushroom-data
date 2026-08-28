import datetime as dt
import hashlib

from config import UN_COMTRADE_API_KEY
from utils import log, post_to_site, safe_get


SOURCES = (
    {"id": "uz_statistics_monthly", "countries": ("UZ",),
     "name": "乌兹别克斯坦国家统计委员会", "url": "https://stat.uz/en/official-statistics/merchandise-trade",
     "probe_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_3088.json",
     "role": "importer_official_control",
     "scope": "按月发布的两位商品编码进口额，用于核验食用菌所属章节的市场变化"},
    {"id": "uz_customs", "countries": ("UZ",), "name": "乌兹别克斯坦海关委员会",
     "url": "https://customs.uz/en", "role": "customs_official_control",
     "scope": "官方货物外贸统计与消费品进口信息，用于国家统计口径交叉核验"},
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
    {"id": "lao_trade_portal", "countries": ("LA",), "name": "老挝国家贸易门户",
     "url": "https://www.laotradeportal.gov.la/en-gb/site/searchcommodity",
     "role": "customs_tariff_control",
     "scope": "AHTN 2022 十位税则、进口税率、贸易措施与清关规则核验"},
    {"id": "vn_customs", "countries": ("VN",), "name": "越南海关",
     "url": "https://www.customs.gov.vn/index.jsp?CoQuanBH=27&pageid=241",
     "role": "customs_official_control",
     "scope": "越南海关月度进出口统计与商品贸易公告核验"},
    {"id": "th_customs_open_data", "countries": ("TH",), "name": "泰国海关开放数据中心",
     "url": "https://catalog.customs.go.th/dataset/?organization=thaicustoms",
     "role": "customs_official_control",
     "scope": "按 HS、原产国、运输方式和口岸发布的进出口开放数据"},
    {"id": "mm_trade_portal", "countries": ("MM",), "name": "缅甸国家贸易门户",
     "url": "https://www.myanmartradeportal.gov.mm/trade-data-charts",
     "role": "importer_official_control",
     "scope": "正常贸易、边境贸易、商品组、伙伴国和边境站贸易统计核验"},
    {"id": "kh_customs_imts", "countries": ("KH",), "name": "柬埔寨海关国际商品贸易统计",
     "url": "https://stats.customs.gov.kh/en/data-search/by-hs-code",
     "role": "customs_official_control",
     "scope": "按 HS、伙伴国、运输方式发布的月度和年度金额、数量统计"},
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
        is_mirror = source["id"].startswith("un_mirror_")
        headers = {"Ocp-Apim-Subscription-Key": UN_COMTRADE_API_KEY} if is_mirror and UN_COMTRADE_API_KEY else {}
        probe_url = source.get("probe_url", source["url"])
        if is_mirror:
            reporter = {"un_mirror_ru": 643, "un_mirror_kz": 398, "un_mirror_tr": 792}[source["id"]]
            partner = 860 if reporter == 398 else 398
            probe_url = ("https://comtradeapi.un.org/data/v1/get/C/A/HS"
                         f"?period=2024&reporterCode={reporter}&flowCode=X&partnerCode={partner}"
                         "&cmdCode=070951&partner2Code=0&customsCode=C00&motCode=0&maxRecords=50")
        response = None if is_mirror else safe_get(probe_url, headers=headers, retries=3, backoff=3, timeout=45)
        body = response.content if response else b""
        available = bool(UN_COMTRADE_API_KEY) if is_mirror else bool(response and body)
        availability = "configured" if is_mirror and available else "reachable" if available else "unreachable"
        digest = hashlib.sha256(body).hexdigest() if body else None
        for country in source["countries"]:
            post_to_site("/api/ingest/snapshot", {
                "metric": "trade", "country": country, "source": source["name"],
                "data": {"partner_code": "SOURCE_REGISTRY", "source_id": source["id"],
                         "source_name": source["name"], "source_url": source["url"],
                         "source_role": source["role"], "evidence_scope": source["scope"],
                         "supports_hs_partner_api": source["id"].startswith("un_mirror_"),
                         "availability": availability,
                         "content_sha256": digest, "checked_at": checked_at,
                         "status": "live" if available else "gap"}
            })
        log(f"official source {source['id']} {availability}")


if __name__ == "__main__":
    run()
