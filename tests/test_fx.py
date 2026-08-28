import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from fetch_fx import extract_rates


class FxCollectorTest(unittest.TestCase):
    def test_all_target_market_rates_and_cny_cross_are_built(self):
        payload={"rates":{"CNY":7.2,"KZT":500,"UZS":12500,"KGS":87,"TJS":10.8,"TMT":3.5,"LAK":22000,"VND":26000,"THB":32,"MMK":2100,"KHR":4100}}
        rows=extract_rates(payload)
        self.assertEqual(len(rows),10)
        kz=next(row for row in rows if row["country"]=="KZ")
        self.assertEqual(kz["currency"],"KZT")
        self.assertAlmostEqual(kz["local_per_cny"],500/7.2)

    def test_missing_cny_is_rejected(self):
        with self.assertRaises(ValueError):extract_rates({"rates":{"KZT":500}})
