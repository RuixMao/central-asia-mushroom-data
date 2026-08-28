from publish_laos_myanmar_relaxed_retail import ROWS

def test_country_targets_and_traceability():
    counts = {code: sum(row[0] == code for row in ROWS) for code in ("LA", "MM")}
    assert counts["LA"] >= 25
    assert counts["MM"] >= 20
    assert all(row[6] and row[7] and row[10].startswith("https://") for row in ROWS)

def test_no_weight_inference():
    for row in ROWS:
        spec, grams, notes = row[6], row[9], row[12]
        if grams is None:
            assert "未折算" in notes
        else:
            assert str(grams) in spec
