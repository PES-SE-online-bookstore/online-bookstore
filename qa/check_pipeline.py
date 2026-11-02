"""Verify evidence calculations and honest report generation without a database."""

import tempfile
import unittest
from pathlib import Path

from qa.run_validation import read_coverage, write_reports


class ReportingChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.metadata = {
            "commit": "fixture-commit", "tracked_changes": "", "run_id": "fixture-run",
            "started_utc": "2026-01-01T00:00:00+00:00", "platform": "fixture",
            "python": "3.11", "test_exit_code": 1,
        }

    def test_line_and_branch_metrics_remain_distinct(self):
        xml = self.directory / "coverage.xml"
        xml.write_text('<coverage line-rate="0.8" branch-rate="0.25" lines-covered="8" '
                       'lines-valid="10" branches-covered="1" branches-valid="4">'
                       '<packages><package><classes><class filename="accounts/views.py" '
                       'line-rate="0.8" branch-rate="0.25" /></classes></package></packages>'
                       '</coverage>')
        coverage = read_coverage(xml)
        self.assertEqual(coverage["line_percent"], 80)
        self.assertEqual(coverage["branch_percent"], 25)
        write_reports(self.directory, self.metadata, None, coverage)
        code = (self.directory / "reports/Code_Coverage_Report.md").read_text(encoding="utf-8")
        branch = (self.directory / "reports/Branch_Coverage_Report.md").read_text(encoding="utf-8")
        self.assertIn("coverage: 80.00%", code)
        self.assertIn("coverage: 25.00%", branch)
        self.assertIn("test execution failed", code)

    def test_setup_failure_produces_four_incomplete_reports(self):
        self.assertIsNone(read_coverage(self.directory / "missing.xml"))
        write_reports(self.directory, self.metadata, None, None)
        reports = self.directory / "reports"
        self.assertEqual(len(list(reports.glob("*.md"))), 4)
        self.assertIn("Coverage unavailable", (reports / "Code_Coverage_Report.md").read_text())
        self.assertIn("acceptance not established", (reports / "System_Validation_Report.md").read_text(encoding="utf-8"))

    def test_unclassified_tests_are_not_reported_as_unit_tests(self):
        results = {"tests_run": 1, "failures": 0, "errors": 0, "skipped": 0,
                   "expected_failures": 0, "unexpected_successes": 0,
                   "records": [{"test_id": "accounts.tests.Example.test_login", "level": "Unclassified",
                                "requirements": [], "status": "Passed", "seconds": 0.1}]}
        write_reports(self.directory, self.metadata, results, None)
        unit = (self.directory / "reports/Unit_Test_Report.md").read_text()
        unit_section = unit.split("## Unit test outcomes")[1].split("## Integration")[0]
        self.assertIn("No outcomes recorded", unit_section)
        self.assertIn("## Unclassified test outcomes", unit)


if __name__ == "__main__":
    unittest.main(verbosity=2)
