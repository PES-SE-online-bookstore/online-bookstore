"""Django runner that preserves per-test results without guessing test levels."""

import json
import os
import time
import unittest
from pathlib import Path

from django.test.runner import DiscoverRunner


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.active = {}

    def startTest(self, test):
        super().startTest(test)
        self.active[id(test)] = time.monotonic()

    def record(self, test, status, detail=""):
        self.records.append({
            "test_id": test.id(),
            "level": getattr(test, "qa_level", "Unclassified"),
            "requirements": list(getattr(test, "qa_requirements", ())),
            "status": status,
            "detail": detail,
            "seconds": round(time.monotonic() - self.active.get(id(test), time.monotonic()), 6),
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "Passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "Failed", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "Error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "Skipped", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, "Expected failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, "Unexpected success")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "Failed" if issubclass(err[0], test.failureException) else "Error"
            self.record(subtest, status, self._exc_info_to_string(err, test))

    def stopTestRun(self):
        super().stopTestRun()
        directory = Path(os.environ["QA_RUN_DIR"])
        directory.mkdir(parents=True, exist_ok=True)
        result = {
            "tests_run": self.testsRun,
            "successful": self.wasSuccessful(),
            "failures": len(self.failures),
            "errors": len(self.errors),
            "skipped": len(self.skipped),
            "expected_failures": len(self.expectedFailures),
            "unexpected_successes": len(self.unexpectedSuccesses),
            "records": self.records,
        }
        (directory / "test-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


class EvidenceRunner(DiscoverRunner):
    def get_resultclass(self):
        return EvidenceResult
