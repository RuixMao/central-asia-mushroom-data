import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from fetch_event_calendar import calendar_rows


class EventCalendarTest(unittest.TestCase):
    def test_2026_calendar_covers_all_target_countries(self):
        rows=calendar_rows(2026)
        self.assertEqual({row["country"] for row in rows},{"KZ","UZ","KG","TJ","TM","LA","VN","TH","MM","KH"})
        self.assertEqual(len(rows),len({(row["country"],row["name_zh"],row["start_date"]) for row in rows}))
        self.assertTrue(all(row["source_url"].startswith("https://") for row in rows))
        self.assertTrue(all(row["certainty"]=="official" for row in rows))

    def test_unregistered_year_is_not_guessed(self):
        with self.assertRaises(ValueError):calendar_rows(2027)
