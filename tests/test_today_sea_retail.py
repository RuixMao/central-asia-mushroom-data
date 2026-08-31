from publish_today_sea_retail import ROWS


def test_today_sea_rows_cover_every_target_country_and_are_report_ready():
    assert {row[0] for row in ROWS} == {"LA", "VN", "TH", "MM", "KH"}
    assert len(ROWS) >= 30
    assert all(row[4] and row[7] > 0 and row[8] > 0 and row[10].startswith("https://") for row in ROWS)
    assert len({(row[0], row[2], row[4]) for row in ROWS}) == len(ROWS)
