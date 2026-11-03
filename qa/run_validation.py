"""Run from the repository root: python -m qa.run_validation [Django test labels]."""

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def git_output(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "Unavailable"


def run_logged(command, destination, env):
    with destination.open("w", encoding="utf-8") as log:
        log.write("COMMAND: " + " ".join(command) + "\n")
        log.flush()
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
        return process.wait()


def read_coverage(path):
    if not path.exists():
        return None
    root = ET.parse(path).getroot()
    classes = root.findall(".//class")
    names = [node.get("filename", "").replace("\\", "/").removeprefix("./") for node in classes]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate XML file paths; per-file coverage is unsafe")
    packages = {"accounts", "books", "cart", "orders", "config"}
    if any("/" not in name or name.split("/")[0] not in packages for name in names):
        raise ValueError("XML must contain repository-relative package/file.py paths, not basenames")
    lines = [line for node in classes for line in node.findall("./lines/line")]
    line_total = len(lines)
    line_covered = sum(int(line.get("hits", "0")) > 0 for line in lines)
    branch_covered = branch_total = 0
    for line in lines:
        if line.get("branch") == "true":
            match = re.search(r"\((\d+)/(\d+)\)", line.get("condition-coverage", ""))
            if match is None:
                raise ValueError("Branch counts missing from XML")
            branch_covered += int(match[1])
            branch_total += int(match[2])
    observed = (line_covered, line_total, branch_covered, branch_total)
    declared = tuple(int(root.get(key, "0")) for key in
                     ("lines-covered", "lines-valid", "branches-covered", "branches-valid"))
    if observed != declared:
        raise ValueError(f"Per-file counts {observed} do not reconcile with overall totals {declared}")
    def metrics(node):
        return {
            "line_percent": round(float(node.get("line-rate", "0")) * 100, 4),
            "branch_percent": round(float(node.get("branch-rate", "0")) * 100, 4),
        }
    return {
        **metrics(root),
        "lines_covered": int(root.get("lines-covered", "0")),
        "lines_valid": int(root.get("lines-valid", "0")),
        "branches_covered": int(root.get("branches-covered", "0")),
        "branches_valid": int(root.get("branches-valid", "0")),
        "files": [{"file": name, **metrics(node)} for name, node in zip(names, classes)],
    }


def export_register(directory, results):
    """Execution evidence only; requirement acceptance is never inferred."""
    records = results.get("records", []) if results else []
    with (directory / "executions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fields = ["test_id", "level", "requirements", "status", "seconds", "mapping_basis"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {key: record.get(key, "") for key in fields}
            row["requirements"] = "; ".join(row["requirements"])
            writer.writerow(row)
    requirement_ids = ([f"BOOK-F-{n:03}" for n in range(1, 21)] +
                       [f"BOOK-NF-{n:03}" for n in range(1, 7)] +
                       [f"BOOK-SR-{n:03}" for n in range(1, 6)])
    with (directory / "traceability.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["requirement_id", "mapped_outcomes", "passed", "failed_or_error",
                         "verification_status", "test_ids"])
        for requirement in requirement_ids:
            selected = [r for r in records if requirement in r["requirements"]]
            failed = sum(r["status"] in ("Failed", "Error", "Unexpected success") for r in selected)
            status = "Failed automated check; review defect" if failed else (
                "Partial automated evidence; acceptance pending" if selected else "Not verified")
            writer.writerow([requirement, len(selected), sum(r["status"] == "Passed" for r in selected),
                             failed, status, "; ".join(r["test_id"] for r in selected)])
    with (directory / "defect-candidates.md").open("w", encoding="utf-8") as handle:
        handle.write("# Automated defect candidates\n\nReview and reproduce before filing; no Jira issues were created.\n\n")
        for record in records:
            if record["status"] not in ("Failed", "Error", "Unexpected success"):
                continue
            handle.write(f"## {record['test_id']}\n\nRequirements: {', '.join(record['requirements'])}.\n\n")
            handle.write("```text\n" + record.get("detail", "") + "\n```\n\n")


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_reports(directory, metadata, results, coverage):
    reports = directory / "reports"
    reports.mkdir(exist_ok=True)
    common = (f"Source commit: `{metadata['commit']}`\n\n"
              f"Tracked changes: {cell(metadata['tracked_changes'] or 'None')}\n\n"
              f"Run: `{metadata['run_id']}`; started: {metadata['started_utc']}\n\n"
              f"Environment: {metadata['platform']}; Python {metadata['python']}\n\n"
              f"Settings: `{metadata.get('settings', 'Not recorded')}`\n\n"
              f"Test process exit code: {metadata.get('test_exit_code', 'Not started')}\n\n"
              "Evidence applies to this source and test environment. The deployed version is unverified.\n\n")
    if metadata.get("settings") == "qa.settings_local":
        common += ("DIAGNOSTIC RUN: SQLite with test-only static-file storage. This does not verify "
                   "PostgreSQL locking/concurrency, production settings, or deployed browser behavior.\n\n")
    if metadata.get("coverage_integrity_error"):
        common += "Coverage integrity error: " + cell(metadata["coverage_integrity_error"]) + "\n\n"
    records = results.get("records", []) if results else []
    unit = "# Unit Test Report\n\n" + common
    if results:
        unit += (f"Executed test methods: {results['tests_run']}; failures: {results['failures']}; "
                 f"errors: {results['errors']}; skipped: {results['skipped']}; "
                 f"expected failures: {results['expected_failures']}; "
                 f"unexpected successes: {results['unexpected_successes']}.\n\n")
    else:
        unit += "No structured test result was produced. Inspect tests.log for setup/discovery failures.\n\n"
    unit += ("Only explicitly classified tests count as unit tests. Existing unclassified tests need review; "
             "request/database tests must not automatically be called unit tests.\n\n")
    for level in ("Unit", "Integration", "System", "Unclassified"):
        selected = [r for r in records if r["level"] == level]
        unit += f"## {level} test outcomes\n\n"
        if not selected:
            unit += "No outcomes recorded in this category.\n\n"
            continue
        unit += "| Test | Result | Seconds | Requirement IDs |\n|---|---|---:|---|\n"
        for record in selected:
            unit += (f"| {cell(record['test_id'])} | {record['status']} | {record['seconds']} | "
                     f"{cell(', '.join(record['requirements']) or 'Not mapped')} |\n")
        unit += "\n"
    unit += "Failure details: ../test-results.json and ../tests.log. Open defects and retests require review.\n"
    (reports / "Unit_Test_Report.md").write_text(unit, encoding="utf-8")

    system = "# System Validation Report\n\n" + common
    system += "Status: INCOMPLETE — automated evidence only; acceptance not established.\n\n"
    system += "## Automated evidence\n\n"
    system += (f"Recorded outcomes by status: {dict(Counter(r['status'] for r in records))}.\n\n"
               "Outcome records may include failing subtests and setup errors; they are not a count of unique cases.\n\n")
    system += "## Required outstanding validation\n\n| Task | Outstanding evidence |\n|---|---|\n"
    outstanding = {
        "OBP-41": "Browser login/logout, real reset-email delivery, authentication requirement acceptance",
        "OBP-42": "Browser catalogue/search/filter/pagination validation",
        "OBP-43": "Browser checkout and genuine sandbox payment verification; mock limits",
        "OBP-44": "Browser order/tracking/cancellation/return validation",
        "OBP-45": "Browser seller/admin ownership and approval validation",
        "OBP-46": "Browser reviews/wishlist and actual notification delivery",
        "OBP-47": "Deployed TLS/cookies, authorization, sensitive-data and security evidence",
        "OBP-48": "Performance/load, accessibility, monthly uptime, backup/restore and recovery timing",
        "OBP-49": "Complete deployed journeys, linked defect retests, final regression",
    }
    for task, text in outstanding.items():
        system += f"| {task} | {text} |\n"
    system += "\nAttach execution IDs, build IDs, evidence and defect links before final acceptance.\n"
    (reports / "System_Validation_Report.md").write_text(system, encoding="utf-8")

    for kind in ("Code", "Branch"):
        content = f"# {kind} Coverage Report\n\n" + common
        content += ("Measured scope: accounts, books, cart, orders, config. Test modules and migrations "
                    "are excluded; exact configuration is stored in coverage-config.txt.\n\n")
        if coverage is None:
            content += "Coverage unavailable. No percentage or pass result can be established.\n"
        else:
            branch = kind == "Branch"
            valid = coverage["branches_valid" if branch else "lines_valid"]
            covered = coverage["branches_covered" if branch else "lines_covered"]
            key = "branch_percent" if branch else "line_percent"
            content += (f"Covered: {covered}; total: {valid}; "
                        f"coverage: {coverage[key]:.2f}%.\n\n" if valid else
                        "No executable opportunities measured; percentage not applicable.\n\n")
            if not branch:
                content += ("The SRS targets 70% of core business logic. This package-wide measurement "
                            "requires an agreed core-logic scope before acceptance is claimed.\n\n")
            else:
                content += "No separate branch threshold is assumed.\n\n"
            if metadata.get("test_exit_code") != 0:
                content += "WARNING: test execution failed; coverage is diagnostic, not successful acceptance evidence.\n\n"
            content += "| File | Coverage % |\n|---|---:|\n"
            for row in coverage["files"]:
                content += f"| {cell(row['file'])} | {row[key]:.2f} |\n"
            content += "\nSource: ../coverage.xml. Missing lines/branches: ../coverage.txt and ../html/index.html.\n"
        (reports / f"{kind}_Coverage_Report.md").write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="*")
    parser.add_argument("--settings", help="Explicit diagnostic settings; omitted in PostgreSQL CI")
    args = parser.parse_args()
    started = utc_now()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = ROOT / "qa-results" / run_id
    directory.mkdir(parents=True)
    metadata = {
        "run_id": run_id, "started_utc": started, "commit": git_output("rev-parse", "HEAD"),
        "tracked_changes": git_output("diff", "HEAD", "--name-only"),
        "untracked_files": git_output("ls-files", "--others", "--exclude-standard"),
        "platform": platform.platform(), "python": platform.python_version(),
        "labels": args.labels or ["Full Django discovery"],
        "settings": args.settings or os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
    }
    source_files = [path for package in ("accounts", "books", "cart", "orders", "config", "qa")
                    for path in (ROOT / package).rglob("*.py")]
    source_files += [
        ROOT / ".coveragerc",
        ROOT / "requirements.txt",
        ROOT / "render.yaml",
        ROOT / ".github/workflows/ci.yml",
    ]
    (directory / "source-fingerprints.json").write_text(json.dumps({
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source_files)
    }, indent=2), encoding="utf-8")
    env = os.environ.copy()
    env["QA_RUN_DIR"] = str(directory)
    env["COVERAGE_FILE"] = str(directory / ".coverage")
    env["PYTHONUNBUFFERED"] = "1"
    if args.settings:
        env["DJANGO_SETTINGS_MODULE"] = args.settings
    (directory / "coverage-config.txt").write_text((ROOT / ".coveragerc").read_text(), encoding="utf-8")
    run_logged([sys.executable, "-m", "pip", "freeze"], directory / "packages.txt", env)
    command = [sys.executable, "-m", "coverage", "run", "manage.py", "test", *args.labels,
               "--noinput", "--verbosity", "2", "--testrunner=qa.runner.EvidenceRunner"]
    metadata["test_command"] = command
    metadata["test_exit_code"] = run_logged(command, directory / "tests.log", env)
    report_commands = {
        "text": ["report", "-m"],
        "xml": ["xml", "-o", str(directory / "coverage.xml")],
        "html": ["html", "-d", str(directory / "html")],
    }
    metadata["coverage_exit_codes"] = {}
    for name, arguments in report_commands.items():
        log_name = "coverage.txt" if name == "text" else f"coverage-{name}.log"
        metadata["coverage_exit_codes"][name] = run_logged(
            [sys.executable, "-m", "coverage", *arguments], directory / log_name, env)
    results_path = directory / "test-results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else None
    try:
        coverage = read_coverage(directory / "coverage.xml")
    except (ValueError, ET.ParseError) as exc:
        coverage = None
        metadata["coverage_integrity_error"] = str(exc)
        (directory / "coverage-integrity-error.txt").write_text(str(exc), encoding="utf-8")
    metadata["finished_utc"] = utc_now()
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if coverage is not None:
        (directory / "coverage-summary.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    write_reports(directory, metadata, results, coverage)
    export_register(directory, results)
    print(f"\nEvidence and reports: {directory}")
    good = (metadata["test_exit_code"] == 0 and results is not None and results["tests_run"] > 0
            and results["successful"] and coverage is not None
            and all(code == 0 for code in metadata["coverage_exit_codes"].values()))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
