import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from fetch_sea_logistics import corridor_rows


class SoutheastAsiaLogisticsTest(unittest.TestCase):
    def test_all_five_markets_have_official_corridor_records(self):
        rows = corridor_rows(probe=False)
        self.assertEqual({row["country"] for row in rows}, {"LA", "VN", "TH", "MM", "KH"})
        self.assertTrue(all(row["source_url"].startswith("https://") for row in rows))
        self.assertTrue(all(row["frontier_posts"] and row["asean_highways"] for row in rows))
        self.assertTrue(all(row["transit_days"] is None and row["freight_rate"] is None for row in rows))


if __name__ == "__main__":
    unittest.main()
