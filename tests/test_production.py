import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

import fetch_production


class Response:
    def json(self):
        return {"data": [{"Year": 2024, "Value": 123.5, "Flag": "I"}]}


class ProductionTest(unittest.TestCase):
    @patch.dict("os.environ", {"COUNTRY": "KZ", "DRY_RUN": "false"}, clear=False)
    @patch("fetch_production.post_to_site")
    @patch("fetch_production.safe_get", return_value=Response())
    def test_faostat_estimate_flag_is_preserved(self, _get, post):
        fetch_production.run()
        payload = post.call_args.args[1]
        self.assertEqual(payload["metric"], "production")
        self.assertEqual(payload["data"]["flag"], "I")
        self.assertTrue(payload["data"]["is_estimate"])
        self.assertEqual(payload["data"]["value_tonnes"], 123.5)

    @patch.dict("os.environ", {"COUNTRY": "KZ", "DRY_RUN": "false"}, clear=False)
    @patch("fetch_production.post_to_site")
    @patch("fetch_production.safe_get", return_value=None)
    def test_unreachable_source_writes_gap_not_zero(self, _get, post):
        fetch_production.run()
        payload = post.call_args.args[1]
        self.assertEqual(payload["data"]["status"], "gap")
        self.assertEqual(payload["data"]["reason"], "unreachable")
        self.assertNotIn("value_tonnes", payload["data"])


if __name__ == "__main__":
    unittest.main()
