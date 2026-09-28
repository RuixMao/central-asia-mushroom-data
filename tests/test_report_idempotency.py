import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

import generate_report


class ReportPublicationDateTests(unittest.TestCase):
    def test_utc_timestamp_crosses_shanghai_midnight_and_overrides_slug(self):
        report = {
            "publishedAt": "2026-09-27T16:00:00Z",
            "slug": "2026-09-27-report",
        }
        self.assertEqual(generate_report.report_publication_date(report), "2026-09-28")

    def test_before_midnight_and_explicit_offsets(self):
        for timestamp in ("2026-09-27T15:59:59.999Z", "2026-09-27T23:59:59+08:00"):
            with self.subTest(timestamp=timestamp):
                self.assertEqual(generate_report.report_publication_date({"publishedAt": timestamp}), "2026-09-27")

    def test_database_milliseconds(self):
        milliseconds = datetime(2026, 9, 27, 16, tzinfo=timezone.utc).timestamp() * 1000
        self.assertEqual(generate_report.report_publication_date({"publishedAt": milliseconds}), "2026-09-28")

    def test_missing_or_invalid_timestamp_uses_valid_slug_date(self):
        for value in (None, "bad timestamp", "2026-13-01T00:00:00Z"):
            with self.subTest(value=value):
                self.assertEqual(generate_report.report_publication_date({"publishedAt": value, "slug": "2026-09-28-report"}), "2026-09-28")

    def test_invalid_slug_or_title_only_cannot_claim_today(self):
        for report in (
            {"slug": "2026-02-31-report"},
            {"slug": "x2026-09-28-report"},
            {"title": "食用菌出海市场日报｜9月28日：市场平稳无异常"},
            {"title": "2026-09-28", "slug": "2026-09-27-report"},
        ):
            with self.subTest(report=report):
                self.assertNotEqual(generate_report.report_publication_date(report), "2026-09-28")


class ReportRunIdempotencyTests(unittest.TestCase):
    current = {
        "title": "食用菌出海市场日报｜9月28日：市场平稳无异常",
        "summary": "原摘要",
        "body": "原正文",
        "slug": "2026-09-27-report",
        "publishedAt": "2026-09-27T16:15:00Z",
    }

    def test_repeat_run_reuses_artifact_without_prices_ai_or_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts" / "daily-report.json"
            with patch.dict(os.environ, {"REPORT_REVISION": "false", "REPORT_ARTIFACT_OUTPUT": str(output)}), \
                    patch.object(generate_report, "datetime") as clock, \
                    patch.object(generate_report, "get_site", return_value={"records": [self.current]}) as get, \
                    patch.object(generate_report, "post_to_site") as post, \
                    patch.object(generate_report, "OpenAI") as ai:
                clock.now.return_value = datetime(2026, 9, 28, 0, 30)
                clock.fromisoformat.side_effect = datetime.fromisoformat
                generate_report.run()
                get.assert_called_once_with("/api/ingest/report?type=daily")
                post.assert_not_called()
                ai.assert_not_called()
            artifact = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(artifact, {**{key: self.current[key] for key in ("title", "summary", "body", "slug")}, "date": "2026-09-28"})

    def test_revision_bypasses_same_day_skip(self):
        with patch.dict(os.environ, {"REPORT_REVISION": "true", "REPORT_ARTIFACT_OUTPUT": ""}), \
                patch.object(generate_report, "datetime") as clock, \
                patch.object(generate_report, "get_site", side_effect=[{"records": [self.current]}, {"records": []}]) as get, \
                patch.object(generate_report, "post_to_site") as post:
            clock.now.return_value = datetime(2026, 9, 28, 0, 30)
            clock.fromisoformat.side_effect = datetime.fromisoformat
            with self.assertRaisesRegex(RuntimeError, "没有可用于客户版"):
                generate_report.run()
            self.assertEqual(get.call_count, 2)
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
