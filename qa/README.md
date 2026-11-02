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

Run from the repository root with the configured Python environment. Each run
creates a separate UTC-stamped directory under qa-results, which is ignored by
Git. The command returns nonzero for failed tests, missing results, zero executed
tests or coverage-generation failures. Raw test output and failure details may
contain sensitive test data; review before publication.

## Outputs per run

- metadata.json: source SHA, dirty/untracked state, timestamps, commands and exit codes.
- packages.txt: installed packages, without dumping environment variables.
- tests.log and test-results.json: raw and per-test execution evidence.
- coverage.txt, coverage.xml, coverage-summary.json, html/: coverage evidence.
- reports/Unit_Test_Report.md
- reports/System_Validation_Report.md
- reports/Code_Coverage_Report.md
- reports/Branch_Coverage_Report.md

The four Markdown files are editable report drafts, not final signed PDFs.
System/browser, email delivery, performance/load, accessibility, monthly uptime,
recovery and defect-retest evidence must be added before acceptance.

## Classification and traceability

Existing tests are unclassified until reviewed. For a reviewed test class, set
`qa_level = "Unit"` or `"Integration"` or `"System"`, and set
`qa_requirements = ("BOOK-F-001",)` to declare the requirements the tests really
cover. Attributes can also be attached to a test instance. Do not label an entire
class against requirements that only some methods verify; split classes or use
per-test metadata. Metadata is not proof of complete requirement acceptance.

Line and branch percentages are extracted separately from coverage XML. No
branch threshold is invented. Agree on the definition of core business logic
before applying the SRS 70% acceptance target to this package-wide measurement.
