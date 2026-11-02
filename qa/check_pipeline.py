"""Verify evidence calculations and honest report generation without a database."""

import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

from qa.run_validation import read_coverage, write_reports


class ReportingChecks(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent.parent / "qa-results" / "tool-checks"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.metadata = {
            "commit": "fixture-commit", "tracked_changes": "", "run_id": "fixture-run",
            "started_utc": "2026-01-01T00:00:00+00:00", "platform": "fixture",
            "python": "3.11", "test_exit_code": 1,
        }

    def test_line_and_branch_metrics_remain_distinct(self):
        xml = self.directory / "coverage.xml"
        lines = ''.join(f'<line number="{n}" hits="{int(n <= 8)}"' +
                        (' branch="true" condition-coverage="25% (1/4)"' if n == 1 else '') + '/>'
                        for n in range(1, 11))
        xml.write_text('<coverage line-rate="0.8" branch-rate="0.25" lines-covered="8" '
                       'lines-valid="10" branches-covered="1" branches-valid="4">'
                       '<packages><package><classes><class filename="accounts/views.py" '
                       'line-rate="0.8" branch-rate="0.25"><lines>' + lines + '</lines></class></classes></package></packages>'
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

    def test_basename_only_xml_is_rejected(self):
        xml = self.directory / "coverage.xml"
        xml.write_text('<coverage><packages><package><classes><class filename="views.py" />'
                       '</classes></package></packages></coverage>')
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            read_coverage(xml)

    def test_incomplete_xml_totals_are_rejected(self):
        xml = self.directory / "coverage.xml"
        xml.write_text('<coverage lines-valid="20"><packages><package><classes>'
                       '<class filename="accounts/views.py"><lines><line number="1" hits="0" />'
                       '</lines></class></classes></package></packages></coverage>')
        with self.assertRaisesRegex(ValueError, "reconcile"):
            read_coverage(xml)

    def test_real_coverage_preserves_same_named_modules(self):
        """Regression for AUTO-001: two views.py files must survive XML generation."""
        project = self.directory
        config = Path(__file__).resolve().parent.parent / ".coveragerc"
        (project / ".coveragerc").write_text(config.read_text())
        for name in ("accounts", "books"):
            package = project / name
            package.mkdir()
            (package / "__init__.py").write_text("")
            (package / "views.py").write_text("def choose(value):\n    if value:\n        return 1\n    return 0\n")
        (project / "driver.py").write_text("from accounts.views import choose\nfrom books.views import choose as other\nchoose(True)\nother(False)\n")
        for arguments in (["run", "driver.py"], ["xml", "-o", "coverage.xml"]):
            result = subprocess.run([sys.executable, "-m", "coverage", *arguments], cwd=project,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        coverage = read_coverage(project / "coverage.xml")
        filenames = {row["file"] for row in coverage["files"]}
        self.assertIn("accounts/views.py", filenames)
        self.assertIn("books/views.py", filenames)


if __name__ == "__main__":
    unittest.main(verbosity=2)
