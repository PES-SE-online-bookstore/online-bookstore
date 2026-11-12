# Unit Test Report

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

**18 Unit tests Passed.** The full Django suite contains 294 tests: 18 Unit and 276 Integration. Zero failures, errors, skipped tests, expected failures or unexpected successes. Python 3.11.18; the hosted workflow uses PostgreSQL 18.

| Test ID | Result | Requirement mapping |
|---|---|---|
| accounts.test_authentication.RegistrationValidationUnitTests.test_admin_role_cannot_be_selected | Passed | BOOK-F-001, BOOK-SR-004 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_duplicate_email_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_duplicate_username_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_email_is_normalized | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_invalid_email_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_mismatched_password_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_numeric_password_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_short_password_is_rejected | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_username_is_trimmed | Passed | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_valid_registration_passes_validation | Passed | BOOK-F-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_fails_when_connection_is_not_encrypted | Passed | BOOK-SR-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_rejects_non_postgresql_database | Passed | BOOK-SR-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_reports_tls_version_and_cipher | Passed | BOOK-SR-001 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_api_failures_raise_sanitized_backend_error | Passed | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_empty_message_list_does_not_make_api_requests | Passed | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_fail_silently_returns_zero_on_api_failure | Passed | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_missing_oauth_credentials_raise_configuration_error | Passed | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_sends_email_through_gmail_https_api | Passed | BOOK-F-020, BOOK-SR-001 |

The full-suite duration was **66.125 seconds**, not a unit-only duration or a website response time. The Unit groups cover registration validation, mocked database-TLS command reporting and mocked Gmail HTTPS backend behavior. Mock results do not replace live TLS or inbox-delivery evidence. Exact IDs, timing and classifications are retained in `supporting/Automated_Test_Register.json`. All 294 original assertion outcomes were preserved; tests were not skipped or weakened to hide failures.
