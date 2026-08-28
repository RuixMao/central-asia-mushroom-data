"""Register official Southeast Asia corridors and customs posts.

These records describe verified infrastructure only. Transit days and freight
rates are deliberately omitted until a dated carrier quotation is available.
"""

import datetime as dt

from utils import log, post_to_site, safe_get


ACTS_URL = "https://acts.asean.org/traders-guide/designated-routes-and-customs-office"
RAIL_URL = "https://www.ndrc.gov.cn/xwdt/gdzt/zltl/202206/t20220629_1329402.html"

CORRIDORS = {
    "LA": {"route": "昆明—磨憨—磨丁—万象", "mode": "铁路/公路",
           "frontier_posts": ["磨憨铁路口岸", "磨丁铁路口岸", "万象南站"],
           "asean_highways": ["AH3", "AH12", "AH11", "AH15", "AH16"],
           "source_url": RAIL_URL},
    "VN": {"route": "中国—越南—河内/海防/胡志明市", "mode": "公路/海运",
           "frontier_posts": ["Cau Treo", "Lao Bao", "Moc Bai"],
           "asean_highways": ["AH1", "AH15", "AH16", "AH17"],
           "source_url": ACTS_URL},
    "TH": {"route": "中国—老挝—泰国—曼谷/林查班", "mode": "铁路/公路/海运",
           "frontier_posts": ["Nong Khai", "Chiang Khong", "Mae Sai", "Mae Sot"],
           "asean_highways": ["AH1", "AH2", "AH3", "AH12", "AH16", "AH19"],
           "source_url": ACTS_URL},
    "MM": {"route": "中国—缅甸—曼德勒/仰光", "mode": "公路/海运",
           "frontier_posts": ["Tachileik", "Myawaddy"],
           "asean_highways": ["AH1", "AH2", "AH3", "AH14"],
           "source_url": ACTS_URL},
    "KH": {"route": "中国—越南/泰国—金边/西哈努克港", "mode": "公路/海运",
           "frontier_posts": ["Poi Pet", "Bavet", "Trapeing Kreal", "Sihanoukville International Port"],
           "asean_highways": ["AH1", "AH11"],
           "source_url": ACTS_URL},
}


def corridor_rows(probe=True):
    checked_at = dt.datetime.now(dt.timezone.utc).isoformat()
    availability = {}
    for url in {row["source_url"] for row in CORRIDORS.values()}:
        response = safe_get(url, retries=2, timeout=45) if probe else True
        availability[url] = "reachable" if response else "unreachable"
    return [{"country": country, **row, "source_type": "official_corridor_registry",
             "availability": availability[row["source_url"]], "status": "live",
             "checked_at": checked_at, "transit_days": None, "freight_rate": None}
            for country, row in CORRIDORS.items()]


def run():
    for row in corridor_rows():
        country = row.pop("country")
        post_to_site("/api/ingest/snapshot", {"metric": "logistics", "country": country,
                     "source": "ASEAN指定通道/官方铁路资料", "data": row})
    log(f"Southeast Asia official corridors written: {len(CORRIDORS)}")


if __name__ == "__main__":
    run()
