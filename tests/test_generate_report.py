import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from generate_report import display_usd_per_kg


def test_display_usd_per_kg_formats_numeric_price():
    assert display_usd_per_kg("42.84") == "42.84"


def test_display_usd_per_kg_handles_missing_or_invalid_price():
    assert display_usd_per_kg(None) == "—"
    assert display_usd_per_kg("") == "—"
