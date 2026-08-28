import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from fetch_laos_trade import collect, market_summaries


class LaosTradeTest(unittest.TestCase):
    def test_importer_total_and_mirror_lower_bound_stay_separate(self):
        def fetch(year, reporter, flow, partner):
            if year == 2023 and reporter == 418:
                return [{"cmdCode": "070959", "primaryValue": 164226.70, "netWgt": 197589},
                        {"cmdCode": "200310", "primaryValue": 184.27, "netWgt": 45.24}]
            if year == 2024 and reporter == 764:
                return [{"cmdCode": "070959", "primaryValue": 686705.34, "netWgt": 1721983}]
            return []
        summaries = market_summaries(collect(fetch=fetch, years=(2023, 2024), pause=0))
        official, mirror = summaries
        self.assertEqual(official["market_size_usd"], 164410.97)
        self.assertEqual(official["market_size_basis"], "importer_official")
        self.assertIsNone(mirror["market_size_usd"])
        self.assertEqual(mirror["estimate_lower_usd"], 686705.34)
        self.assertEqual(mirror["confirmed_partners"], ["泰国"])


if __name__ == "__main__":
    unittest.main()
