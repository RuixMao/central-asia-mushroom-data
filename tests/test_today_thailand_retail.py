from publish_today_thailand_retail import ROWS

def test_verified_today_thailand_rows_are_report_ready():
    assert len(ROWS) >= 10
    assert all(row[3] and row[4] > 0 and row[5] > 0 and row[6].startswith("https://") for row in ROWS)
    assert len({(row[0], row[2]) for row in ROWS}) == len(ROWS)
