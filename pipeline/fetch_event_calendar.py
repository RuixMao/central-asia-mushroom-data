"""中亚五国官方非工作日事件日历。

只收录官方政府、劳动部门或官方法库已明确的非工作日；文化纪念日不自动
标记为物流风险。年度调休和宗教节日以当年官方文件为准。
"""

import datetime as dt

from utils import log, post_to_site

SOURCES = {
    "KZ": "https://www.gov.kz/article/33969?lang=en",
    "UZ": "https://my.gov.uz/en/day-off",
    "KG": "https://mlsp.gov.kg/media-fajldar-2/",
    "TJ": "https://mmih.adlia.tj/SEARCH/DocumentView?DocumentId=114933",
    "TM": "https://oilgas.gov.tm/en/posts/news/15758/the-ministry-of-labor-of-turkmenistan-has-published-a-production-calendar-for-2026",
}

# 2026 年已由官方年度日历、劳动部门通知或官方法库确认的非工作日。
# start/end 均为闭区间；只写对办公、银行、政府窗口和清关排班有潜在影响的日期。
HOLIDAYS_2026 = {
    "KZ": [
        ("新年", "2026-01-01", "2026-01-02"), ("东正教圣诞节", "2026-01-07", "2026-01-07"),
        ("国际妇女节及调休", "2026-03-08", "2026-03-09"), ("纳吾肉孜节及调休", "2026-03-21", "2026-03-25"),
        ("人民团结日", "2026-05-01", "2026-05-01"), ("祖国保卫者日", "2026-05-07", "2026-05-07"),
        ("胜利日及调休", "2026-05-09", "2026-05-11"), ("古尔邦节首日", "2026-05-27", "2026-05-27"),
        ("首都日", "2026-07-06", "2026-07-06"), ("共和国日及调休", "2026-10-25", "2026-10-26"),
        ("独立日", "2026-12-16", "2026-12-16"),
    ],
    "UZ": [
        ("新年假期", "2026-01-01", "2026-01-04"), ("国际妇女节及调休", "2026-03-07", "2026-03-09"),
        ("开斋节与纳吾肉孜节假期", "2026-03-20", "2026-03-23"), ("纪念与荣誉日及调休", "2026-05-09", "2026-05-11"),
        ("古尔邦节假期", "2026-05-27", "2026-05-31"), ("独立日假期", "2026-08-29", "2026-09-01"),
        ("教师和导师日", "2026-10-01", "2026-10-01"), ("宪法日", "2026-12-08", "2026-12-08"),
    ],
    "KG": [
        ("新年假期", "2026-01-01", "2026-01-11"), ("国际妇女节", "2026-03-08", "2026-03-08"),
        ("开斋节", "2026-03-20", "2026-03-20"), ("诺鲁孜节", "2026-03-21", "2026-03-21"),
        ("五月假期", "2026-05-01", "2026-05-08"), ("独立日", "2026-08-31", "2026-08-31"),
    ],
    "TJ": [
        ("新年", "2026-01-01", "2026-01-02"), ("母亲节", "2026-03-08", "2026-03-08"),
        ("纳吾肉孜节", "2026-03-21", "2026-03-24"), ("国际劳动节", "2026-05-01", "2026-05-01"),
        ("胜利日", "2026-05-09", "2026-05-09"), ("民族团结日", "2026-06-27", "2026-06-27"),
        ("独立日", "2026-09-09", "2026-09-09"), ("宪法日", "2026-11-06", "2026-11-06"),
    ],
    "TM": [
        ("新年", "2026-01-01", "2026-01-01"), ("国际妇女节", "2026-03-08", "2026-03-08"),
        ("开斋节", "2026-03-20", "2026-03-20"), ("国家春季节", "2026-03-21", "2026-03-23"),
        ("宪法和国旗日", "2026-05-18", "2026-05-18"), ("古尔邦节", "2026-05-27", "2026-05-29"),
        ("独立日", "2026-09-27", "2026-09-27"), ("纪念日", "2026-10-06", "2026-10-06"),
        ("国际中立日", "2026-12-12", "2026-12-12"),
    ],
}


def calendar_rows(year):
    if year != 2026:
        raise ValueError(f"Official calendar for {year} has not been registered")
    rows=[]
    for country,events in HOLIDAYS_2026.items():
        for name,start,end in events:
            start_date=dt.date.fromisoformat(start);end_date=dt.date.fromisoformat(end)
            rows.append({"country":country,"event_type":"public_holiday","name_zh":name,"start_date":start,"end_date":end,
                         "duration_days":(end_date-start_date).days+1,"non_working":True,
                         "business_impact":"政府、银行及部分企业可能暂停或缩短办公时间",
                         "logistics_impact":"口岸与清关排班可能减少，需提前确认",
                         "certainty":"official","source_url":SOURCES[country],"year":year,"status":"scheduled"})
    return rows


def run():
    year=dt.date.today().year;rows=calendar_rows(year);observed=dt.date.today().isoformat()
    for row in rows:
        post_to_site("/api/ingest/snapshot",{"metric":"event_calendar","country":row["country"],"source":"官方节假日历",
            "data":{**{k:v for k,v in row.items() if k!="country"},"observed_at":observed}})
    log(f"Official holiday calendar written: {len(rows)} events for {year}")


if __name__=="__main__":run()
