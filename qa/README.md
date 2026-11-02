# Online Bookstore QA automation

This tooling measures the checked-out source. It does not test the deployed site
or certify completion of the nine sprint tasks.

## First run in GitHub Actions

Publish these QA files on a branch and open a pull request targeting main. The
existing Django CI workflow runs on that pull request using PostgreSQL and
Python 3.11. No production database credentials are needed.

Open Actions, select the run, inspect the test job and download its `qa-results`
artifact. Keep the workflow URL as evidence. A failed job must not be reported as
a passing suite. Installation/check failures may produce logs but no artifact.

## Local execution

Requires the project dependencies, coverage==7.13.4, and a configured development
PostgreSQL database whose user can create the isolated Django test database.
Do not point this tooling at the production database. Existing project settings
read DJANGO_SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST and DB_PORT.

```text
python -m qa.check_pipeline
python -m qa.run_validation
python -m qa.run_validation accounts
```

For optional local diagnostics when PostgreSQL is unavailable:

```text
.qa-venv\Scripts\python.exe -m qa.run_validation accounts.test_authentication --settings=qa.settings_local
```

The diagnostic settings use an isolated in-memory SQLite database and ordinary
static-file storage. They do not alter production settings or the PostgreSQL CI
job. SQLite results do not prove PostgreSQL locks/concurrency or deployed behavior.
The interpreter and installed versions are recorded; CI remains authoritative for
the project's Python 3.11/PostgreSQL environment.

Run from the repository root with the configured Python environment. Each run
creates a separate UTC-stamped directory under qa-results, which is ignored by
Git. The command returns nonzero for failed tests, missing results, zero executed
tests or coverage-generation failures. Raw test output and failure details may
contain sensitive test data; review before publication.

## Outputs per run

- metadata.json: source SHA, dirty/untracked state, timestamps, commands and exit codes.
- source-fingerprints.json: SHA-256 hashes of application/test/tool source files.
- packages.txt: installed packages, without dumping environment variables.
- tests.log and test-results.json: raw and per-test execution evidence.
- coverage.txt, coverage.xml, coverage-summary.json, html/: coverage evidence.
- executions.csv and traceability.csv: local execution and partial-requirement registers.
- defect-candidates.md: failed automated checks to reproduce/review before Jira filing.
- reports/Unit_Test_Report.md
- reports/System_Validation_Report.md
- reports/Code_Coverage_Report.md
- reports/Branch_Coverage_Report.md

The four Markdown files are editable report drafts, not final signed PDFs.
System/browser, email delivery, performance/load, accessibility, monthly uptime,
recovery and defect-retest evidence must be added before acceptance.

## Classification and traceability

Legacy database/request/service classes are reviewed in qa/catalog.py and are
classified as Integration. Some mappings are explicitly characterization/support
only: mock payments do not verify gateway acceptance, and a health endpoint does
not prove monthly uptime. New isolated form-validation tests use Unit; HTTP and
database authentication tests use Integration. No automated test is called a
deployed System test. For a reviewed test class, set
`qa_level = "Unit"` or `"Integration"` or `"System"`, and set
`qa_requirements = ("BOOK-F-001",)` to declare the requirements the tests really
cover. Attributes can also be attached to a test instance. Do not label an entire
class against requirements that only some methods verify; split classes or use
the per-method @requirement(...) decorator from qa.catalog. Metadata is not proof
of complete requirement acceptance. The generated traceability file never turns
passing supporting tests into full requirement acceptance.

Line and branch percentages are extracted separately from coverage XML. No
branch threshold is invented. Agree on the definition of core business logic
before applying the SRS 70% acceptance target to this package-wide measurement.

## Coverage path integrity

Collection uses the repository as one source root; report includes retain the
same five application/config packages. XML paths must contain package/file.py.
Duplicate/basename paths and per-file counts that do not reconcile with overall
totals fail the run and suppress coverage tables. qa.check_pipeline includes a
real coverage regression with two same-named views.py files.

## AUTO-001 baseline

The original CI artifact is preserved locally under qa-results/baselines/AUTO-001
with a SHA-256 manifest. It must not be edited. Its overall totals are usable as
baseline evidence, but its original basename-only XML per-file tables are invalid.

## Expected OBP-41 acceptance failures

accounts/test_authentication.py contains literal SRS checks for email login and
30-minute reset expiry. They may make CI red until the developer fixes the
implementation or the requirements owner formally changes the requirement. No
expectedFailure decorators or timeout overrides hide these findings. In-memory
email tests prove generation/consumption, not real mailbox delivery. Browser and
real-email results remain outstanding; do not close OBP-41 on these tests alone.
