import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from fetch_uz_official_trade import extract_chapters


class UzbekistanOfficialTradeTests(unittest.TestCase):
    def test_extracts_latest_month_for_required_chapters(self):
        payload = [{"data": [
            {"Code": "7", "Klassifikator_en": "Edible vegetables", "2026-M05": 10.0, "2026-M06": 12.5},
            {"Code": "20", "Klassifikator_en": "Preparations", "2026-M06": 4.2},
            {"Code": "62", "2026-M06": 99.0},
        ]}]
        rows = extract_chapters(payload)
        self.assertEqual([row["chapter"] for row in rows], ["07", "20"])
        self.assertEqual(rows[0]["period"], "2026-M06")
        self.assertEqual(rows[0]["value_usd"], 12500.0)


if __name__ == "__main__":
    unittest.main()
