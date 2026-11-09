# OBP-41 findings awaiting PostgreSQL CI and deployment verification

These are local diagnostic findings, not created Jira issues. Application code
has not been changed. Initial execution used Django 5.2.18, Python 3.12.14 and an
isolated SQLite database; rerun on CI's Python 3.11/PostgreSQL before finalizing
the environment-specific evidence. No real emails were sent.

## QA-AUTH-001 Email login does not establish a session

- Requirement: BOOK-F-002. Development story: OBP-3. Test task: OBP-41.
- Test: accounts.test_authentication.LoginIntegrationTests.test_srs_email_and_password_establish_session
- Preconditions: active buyer with different username and email; known password.
- Steps: submit the registered email and correct password to the login form.
- Expected: authenticated session, as specified by the SRS.
- Observed: no authenticated session. Username login passes a separate current-behavior test.
- Recommendation: developer implements the agreed email authentication contract,
  or requirements owner explicitly revises the requirement. Do not replace this
  assertion with a username-login assertion to hide the discrepancy.

## QA-AUTH-002 Reset link is usable after 30 minutes

- Requirement: BOOK-F-004. Development story: OBP-5. Test task: OBP-41.
- Test: accounts.test_authentication.PasswordResetIntegrationTests.test_srs_link_expires_after_thirty_minutes
- Preconditions: active user; generated reset link; no password change or token use.
- Steps: generate the real application token at controlled time; request it at +1801 seconds.
- Expected: invalid/expired link under the 30-minute acceptance criterion.
- Observed: the reset form accepts the link as valid.
- Recommendation: developer configures expiry to match the agreed requirement.
  Retest valid-before-expiry, expired-after-boundary, tampering, reuse and successful reset.

## Disposition (added 2026-11-09; findings above left as originally written)

- Both findings were confirmed on PostgreSQL / Python 3.11.9 in run
  20261103T063353040577Z (`qa/history/2026-11-03_run_29049b0.md`).
- QA-AUTH-001: resolved by requirement revision R-001
  (`qa/REQUIREMENT_REVISIONS.md`, approval pending), not by code. The email-login
  test was replaced by revised-requirement tests; one asserts an email
  identifier is rejected, so the change is visible rather than hidden.
- QA-AUTH-002: fixed by `PASSWORD_RESET_TIMEOUT = 1800` in `config/settings.py`.
  The +1801 s assertion is unchanged. Retest results must cite a new run ID.

## Remaining OBP-41 evidence

- PostgreSQL CI execution and final source/deployment commit alignment.
- Actual browser cookies, redirects, logout/protected-page behavior.
- Actual email delivery and reset journey through a controlled mailbox.
- PostgreSQL concurrent failed-login updates; SQLite diagnostics cannot verify row locking.
- Linked Jira bugs and retest records once fixes are delivered.
