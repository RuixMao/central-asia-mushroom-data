import json
import tempfile
import unittest
from pathlib import Path

from pipeline.report_sea_coverage import build_report, main


class SoutheastAsiaCoverageTest(unittest.TestCase):
    def test_all_five_countries_are_reported(self):
        rows, reasons = build_report({"summary": {"valid_by_country": {"LA": 2, "TH": 3}}, "errors": []})
        self.assertEqual(dict(rows), {"老挝": 2, "越南": 0, "泰国": 3, "缅甸": 0, "柬埔寨": 0})
        self.assertEqual(reasons, {})

    def test_zero_coverage_warns_without_failing_job(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(json.dumps({"summary": {"valid_by_country": {}}, "errors": []}), encoding="utf-8")
            self.assertEqual(main(path), 0)


if __name__ == "__main__":
    unittest.main()
