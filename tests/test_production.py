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
        self.assertEqual(payload["data"]["estimate_label"], "估算")
        self.assertEqual(payload["data"]["element_code"], 5510)
        self.assertEqual(payload["data"]["value_tonnes"], 123.5)

    @patch.dict("os.environ", {"COUNTRY": "KZ", "DRY_RUN": "false"}, clear=False)
    @patch("fetch_production.post_to_site")
    @patch("fetch_production.safe_get", return_value=None)
    def test_unreachable_source_writes_gap_not_zero(self, _get, post):
        fetch_production.run()
        payload = post.call_args.args[1]
        self.assertEqual(payload["data"]["status"], "gap")
        self.assertEqual(payload["data"]["reason"], "api_and_bulk_unreachable")
        self.assertNotIn("value_tonnes", payload["data"])

    @patch.dict("os.environ", {"COUNTRY": "TM", "DRY_RUN": "false"}, clear=False)
    @patch("fetch_production._bulk_rows", return_value={"TM": []})
    @patch("fetch_production.post_to_site")
    @patch("fetch_production._api_rows", return_value=None)
    def test_missing_faostat_records_keep_local_evidence_separate(self, _api, post, _bulk):
        output = fetch_production.run()
        gap = output[0]
        self.assertEqual(gap["reason"], "no_records")
        self.assertFalse(gap["zero_production"])
        self.assertIn("不代表产量为 0", gap["display_label"])
        records = [row for row in output if row.get("status") == "evidence"]
        self.assertEqual({row["record_type"] for row in records}, {
            "enterprise_output_reported", "production_capacity_planned", "export_status"
        })
        planned = next(row for row in records if row["record_type"] == "production_capacity_planned")
        self.assertFalse(planned["include_in_official_total"])
        export = next(row for row in records if row["record_type"] == "export_status")
        self.assertEqual(export["export_status"], "planned")

    @patch.dict("os.environ", {"COUNTRY": "TJ", "DRY_RUN": "true"}, clear=False)
    @patch("fetch_production._bulk_rows", return_value={"TJ": []})
    @patch("fetch_production._api_rows", return_value=None)
    def test_tajik_evidence_is_not_national_total(self, _api, _bulk):
        output = fetch_production.run()
        evidence = next(row for row in output if row.get("status") == "evidence")
        self.assertEqual(evidence["record_type"], "enterprise_output_reported")
        self.assertFalse(evidence["official_annual_total"])
        self.assertFalse(evidence["include_in_official_total"])


if __name__ == "__main__":
    unittest.main()
