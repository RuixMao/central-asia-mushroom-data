"""price_index 模块单测:指数计算、口径过滤、markdown 渲染。"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))

from price_index import _valid_entries, compute_index, render_markdown, _pct_change


def _rec(country, species, status, local_kg, rate):
    return {
        "price": {"validationStatus": status, "normalizedPricePerKg": local_kg,
                  "usdRateLocalPerUsd": rate},
        "product": {"country": country, "speciesId": species},
    }


def test_valid_entries_filter():
    recs = [
        _rec("KZ", "button_mushroom", "valid", 2000, 500),      # 4 USD/kg ✓
        _rec("KZ", "button_mushroom", "needs_review", 999, 500),  # 非 valid 排除
        _rec("UZ", "oyster_mushroom", "valid", None, 13000),      # 无每公斤价排除
        _rec("KG", "shiitake", "valid", 300, 0),                  # 汇率缺失排除
        _rec("XX", "enoki", "valid", 100, 10),                    # 非五国排除
    ]
    entries = _valid_entries(recs)
    assert entries == [("KZ", "button_mushroom", 4.0)], f"got {entries}"


def test_all_needs_review_group_has_no_aggregate():
    entries = _valid_entries([_rec("KG", "button_mushroom", "needs_review", 3750, 87.54)])
    result = compute_index(entries)
    assert entries == []
    assert "KG" not in result["country_median"]


def test_compute_index():
    entries = [
        ("KZ", "button_mushroom", 4.0), ("KZ", "button_mushroom", 5.0),  # KZ 中位 4.5
        ("UZ", "button_mushroom", 3.0), ("UZ", "oyster_mushroom", 5.0),  # UZ 中位 4.0
    ]
    result = compute_index(entries)
    assert result["base_country"] == "KZ"
    assert result["country_median"]["KZ"] == 4.5
    assert result["country_median"]["UZ"] == 4.0
    assert abs(result["index"]["KZ"] - 100.0) < 1e-6
    assert abs(result["index"]["UZ"] - (4.0 / 4.5 * 100)) < 0.2
    assert result["median_by_species"][("KZ", "button_mushroom")] == 4.5
    # 菌种级指数:KZ 双孢菇=100
    assert abs(result["species_index"]["button_mushroom"]["KZ"] - 100.0) < 1e-6
    assert result["species_index"]["button_mushroom"]["UZ"] > 0


def test_pct_change():
    assert _pct_change(4.5, 4.0) == 12.5
    assert _pct_change(4.0, None) is None
    assert _pct_change(4.0, 0) is None


def test_render_markdown_has_table():
    entries = [("KZ", "button_mushroom", 4.0), ("UZ", "button_mushroom", 3.0)]
    md = render_markdown(compute_index(entries), "2026-08-18")
    assert "双孢菇" in md
    assert "哈萨克斯坦" in md
    assert "|" in md
    # 环比列存在
    assert "周环比" in md


def test_month_change_hook_hidden_without_data():
    """无 30 天前数据时,月环比列整列隐藏(钩子不触发)。"""
    entries = [("KZ", "button_mushroom", 4.0), ("UZ", "button_mushroom", 3.0)]
    md = render_markdown(compute_index(entries), "2026-08-18", month_result=None)
    # 表头行(第一行表格)不应含月环比列;但口径说明里会提及"月环比"文案
    header_line = [l for l in md.splitlines() if l.startswith("| 国家")][0]
    assert "月环比" not in header_line
    assert "周环比" in header_line


def test_month_change_hook_shown_with_data():
    """有 30 天前数据且样本充足时,月环比列自动出现并显示涨跌幅(钩子触发)。"""
    cur = [("KZ", "button_mushroom", 4.0), ("KZ", "button_mushroom", 4.2), ("KZ", "button_mushroom", 3.8),
           ("UZ", "button_mushroom", 3.0), ("UZ", "button_mushroom", 3.1), ("UZ", "button_mushroom", 2.9)]
    month = [("KZ", "button_mushroom", 3.0), ("KZ", "button_mushroom", 3.1), ("KZ", "button_mushroom", 2.9),
             ("UZ", "button_mushroom", 2.0), ("UZ", "button_mushroom", 2.1), ("UZ", "button_mushroom", 1.9)]
    m_prev = compute_index(month)
    m_prev["_day"] = "2026-07-19"
    md = render_markdown(compute_index(cur), "2026-08-18", month_result=m_prev)
    header_line = [l for l in md.splitlines() if l.startswith("| 国家")][0]
    assert "月环比" in header_line
    # KZ 双孢菇中位 4.0 vs 3.0 → +33.3%(国家级综合中位价同样是 4.0 vs 3.0)
    assert "+33.3%" in md


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:
                failed += 1
                print(f"FAIL {name}: {e}")
                traceback.print_exc()
    print(f"\n{failed} failed")
    sys.exit(1 if failed else 0)
