# Test Plan addendum (updates to Software Test Plan v1.0)

Prepared 2026-11-12 for insertion into the Test Plan (the submitted PDF is left
unchanged). It supplies what the Test Plan promises but does not contain: the
test-case table, the updated tool list and scope, and the traceability result.

Evidence base: GitHub Actions run
[43174812573](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43174812573)
on `main` @ `f6d7d85eb6c93599c5e0bd05f6b6560aa1e88da3` (Python 3.11.18,
PostgreSQL): **294 tests executed, 294 passed, 0 failed**; line coverage 91.85%
(1183/1288), branch coverage 84.01% (247/294). Reports and raw data:
`docs/test-reports/`.

## A. Revisions to Test Plan sections

| Section | Submitted text | Revised text |
|---|---|---|
| 4 Features Not to be Tested | "advanced search/caching ... unless later included" | A limited catalogue query-result cache **is** included in the build (OBP-48) and is tested (cases TC-Perf-03 and `books.test_catalogue_cache`). Two-factor login and wishlist price alerts remain out of scope |
| 6 Test Environment: software | "JWT authentication", "Django REST Framework" | Server-rendered Django with session authentication and CSRF protection (see Deviations D-03) |
| 6 Test Environment: tools | "Jenkins for CI/CD; Docker; SonarQube" | GitHub Actions (Django CI on PostgreSQL, daily backup, controlled browsing load, completed-checkout performance, isolated recovery rehearsal); `coverage.py` with the QA reporting tool in `qa/`; Render hosting |
| 6 Test Environment: external services | "Razorpay or Stripe sandbox, SMTP/test email service" | Mock payment gateway (R-002); Gmail HTTPS API for email |
| 11 Assumptions | "Payment testing will use a sandbox/test gateway" | Payment testing uses the in-process mock gateway; gateway acceptance is not verified (R-002) |
| 13 Traceability | "final RTM will be updated" | Requirement-level traceability is generated per run: `docs/test-reports/traceability.csv` (26 requirements with automated evidence, 5 with none) and the table in section B |

## B. Test-case table

Levels follow the Test Plan (Unit / Integration / System). "Result" is the
outcome in run 43174812573 unless stated otherwise. Where there is no automated
evidence the result says so; nothing is shown as passed that has not been run.

### Functional requirements

| TC ID | Requirement | Level | Scenario and expected result | Evidence (automated test or artifact) | Result |
|---|---|---|---|---|---|
| TC-Auth-01 | BOOK-F-001 | Integration | Valid unique registration creates an active account with a Buyer/Seller profile; duplicate email or username creates nothing; a role of ADMIN is refused | `RegistrationIntegrationTests.test_buyer_account_and_profile_are_created`, `.test_duplicate_email_does_not_create_another_account`, `.test_registration_cannot_create_an_admin` | Passed |
| TC-Auth-02 | BOOK-F-002 (revised, R-001) | Integration | Username + correct password creates a session; wrong password and an email identifier do not | `LoginIntegrationTests.test_revised_username_and_password_establish_session`, `.test_email_identifier_is_not_accepted_under_revised_requirement`, `.test_wrong_password_does_not_establish_session` | Passed |
| TC-Auth-03 | BOOK-F-003 | Integration | Fifth consecutive failure locks the account for 15 minutes; the correct password is refused while locked and works after expiry | `LockoutIntegrationTests.test_fifth_failure_locks_for_fifteen_minutes`, `.test_sixth_attempt_shows_lockout_message`, `.test_correct_password_works_after_expiry` | Passed |
| TC-Auth-04 | BOOK-F-004 | Integration | Reset link valid before 30 minutes, invalid after 30 minutes, single use, changes the password | `PasswordResetIntegrationTests.test_link_is_valid_before_thirty_minutes`, `.test_srs_link_expires_after_thirty_minutes`, `.test_used_link_cannot_be_reused`, `.test_successful_reset_changes_password` | Passed (the expiry check failed on 2026-11-03 and was fixed; see `qa/history/`) |
| TC-Cat-01 | BOOK-F-005 | Integration | Catalogue shows 12 books per page, no book omitted or repeated across pages; cover image shown | `CataloguePaginationIntegrationTests.test_first_page_contains_twelve_books`, `.test_three_pages_do_not_omit_or_repeat_books`; `CatalogueRequiredFieldsIntegrationTests.test_srs_catalogue_renders_book_cover_image` | Passed |
| TC-Cat-02 | BOOK-F-006 | Integration | Search by title, author, ISBN, keyword; category and price filters; invalid or reversed price range handled | `BookCatalogueTests.test_search_by_title`, `.test_search_by_isbn`, `.test_filter_by_price_range`, `.test_minimum_price_greater_than_maximum_is_rejected` | Passed |
| TC-Cat-03 | BOOK-F-007 | Integration | Book detail shows seller, price, stock, description and average rating; pending/rejected books return 404 | `CatalogueRequiredFieldsIntegrationTests.test_srs_book_detail_identifies_seller`, `.test_book_detail_displays_computed_average_rating`; `CatalogueVisibilityIntegrationTests.test_pending_book_is_inaccessible_by_direct_url` | Passed |
| TC-Cart-01 | BOOK-F-008 | Integration | Add, update quantity, remove; total recalculated; quantity capped by stock | `CartTests.test_buyer_can_update_quantity`, `.test_buyer_can_remove_item`, `.test_cart_totals_are_calculated_correctly`, `.test_cannot_update_quantity_beyond_stock` | Passed |
| TC-Cart-02 | BOOK-F-009 | Integration | Checkout needs login, a non-empty cart, a valid address and payment method; another buyer's address is refused | `CheckoutTests.test_checkout_requires_login`, `.test_empty_cart_cannot_proceed_to_checkout`, `.test_invalid_payment_method_is_rejected`, `.test_address_belonging_to_another_buyer_is_rejected` | Passed |
| TC-Cart-03 | BOOK-F-010 (mock, R-002) | Integration | Order and pending payment are created; failed initiation marks the payment failed; cart not cleared | `CreateOrderFromCartTests.test_creates_order_items_and_pending_payment`, `.test_failed_initiation_marks_payment_failed`, `.test_order_creation_does_not_clear_cart` | Passed against the **mock** only; gateway acceptance not verified |
| TC-Ord-01 | BOOK-F-011 | Integration | Buyer sees own order history and details; not other buyers' | `OrderHistoryAndDetailTests.test_buyer_can_view_order_history`, `.test_buyer_cannot_view_another_buyers_order` | Passed |
| TC-Ord-02 | BOOK-F-012 | Integration | Tracking page shows the current status for each order state | `ShipmentTrackingTests.test_confirmed_order_shows_confirmed_status`, `.test_shipped_order_shows_shipped_status`, `.test_delivered_order_shows_delivered_status` | Passed (manual status, no shipping API: D-06) |
| TC-Ord-03 | BOOK-F-013 | Integration | Cancellation and return are rejected outside the policy window (7 days) and for shipped orders | `OrderCancellationReturnTests.test_return_request_rejected_after_policy_window`, `.test_shipped_order_cannot_be_cancelled` | Passed |
| TC-Sell-01 | BOOK-F-014 | Integration | Seller creates a PENDING listing; invalid ISBN refused; buyers and anonymous users cannot reach the form | `SellerCreateListingTests.test_seller_can_create_pending_listing`, `.test_invalid_isbn_is_rejected`, `.test_buyer_cannot_access_listing_form` | Passed |
| TC-Sell-02 | BOOK-F-015 | Integration | A seller cannot edit or delete another seller's listing | `SellerEditListingTests.test_seller_cannot_edit_another_sellers_listing`, `SellerDeleteListingTests.test_buyer_cannot_delete_listing` | Passed |
| TC-Admin-01 | BOOK-F-016 | Integration | Admin approves or rejects; only approved listings are public; rejected listings are hidden | `AdminListingApprovalTests.test_admin_can_approve_pending_listing`, `.test_rejected_listing_does_not_appear_in_public_catalogue` | Passed. Seller email notification not implemented (D-07) |
| TC-Admin-02 | BOOK-F-017 | Integration | Deactivated listings and accounts are inaccessible to buyers | `AdminInventoryManagementTests` (class), `LoginIntegrationTests.test_inactive_account_cannot_log_in` | Passed |
| TC-Rev-01 | BOOK-F-018 | Integration | Only a buyer who purchased the book can review; rating 1–5 enforced; average rating shown | `ReviewRolePermissionTests.test_buyer_with_purchase_can_submit_review`, `BookReviewTests.test_invalid_rating_is_rejected` | Passed |
| TC-Rev-02 | BOOK-F-019 | Integration | Wishlist add/remove is POST-only, CSRF-protected, per buyer and idempotent | `SecurityRequestIntegrationTests.test_valid_csrf_wishlist_add_is_idempotent`, `.test_other_buyer_cannot_view_or_remove_saved_item` | Passed |
| TC-Rev-03 | BOOK-F-020 | Integration + Unit | Emails on CONFIRMED, SHIPPED, DELIVERED; none on cancel; a mail failure never blocks the status change; Gmail API backend sends over HTTPS | `OrderEmailNotificationTests.test_confirmed_status_sends_email`, `.test_email_failure_does_not_prevent_status_update`; `GmailAPIEmailBackendTests` (5, mocked HTTP) | Passed. One live delivery confirmed manually on 2026-11-03 |

### Non-functional and security requirements

| TC ID | Requirement | Level | Scenario and expected result | Evidence | Result |
|---|---|---|---|---|---|
| TC-Perf-01 | BOOK-NF-001 | System | Catalogue/search p90 ≤ 3 s under normal load | Workflow "QA Controlled Browsing Load" (`.github/workflows/qa-load.yml`); QA handoff, run 42969189618 | 1, 10, 50 and 100-user stages passed their gates; **the 250-user stage failed** (six HTTP 503s from the platform layer; p90 ≈ 8 s in the aborted sample). Not re-run since the OBP-48 cache. Checkout timing: workflow "QA Completed Checkout Performance" exists; its result is not recorded here |
| TC-Perf-02 | BOOK-NF-002 | System | 500 concurrent users without errors | Same workflow | **Not met / not executed**: the 500-user stage did not begin (D-11) |
| TC-Perf-03 | BOOK-NF-001 (support) | Integration | Catalogue cache: expiry, invalidation, query and session separation, CSP nonce per response, diagnostics headers | `books/test_catalogue_cache.py` (26 tests) | Passed. Verifies correctness only, not capacity |
| TC-Avail-01 | BOOK-NF-003 | Integration | `/health/` returns 200 when the database is reachable and 503 when it is not | `HealthCheckTests.test_health_check_returns_200_when_database_is_available`, `.test_health_check_returns_503_when_database_fails` | Passed. Monthly 99.5% uptime **not measured** |
| TC-UX-01 | BOOK-NF-004 | System | Responsive layout and WCAG 2.1 AA audit | none in the repository | **Not executed** |
| TC-Cov-01 | BOOK-NF-005 | CI | Coverage of core logic ≥ 70% | `docs/test-reports/Code_Coverage_Report.md`, `Branch_Coverage_Report.md` | Package-wide 91.85% line / 84.01% branch; core-logic scope still to be agreed (D-12) |
| TC-Ops-02 | BOOK-NF-006 | System | Daily backup; restore meets RPO 24 h / RTO 4 h | Workflows "Daily Database Backup" and "QA Isolated Recovery Rehearsal" | Workflows exist; **no restore result is recorded in this repository** |
| TC-Sec-01 | BOOK-SR-001 | System + Unit | Plain HTTP is redirected; HSTS set; database connection encrypted; third-party calls verify certificates | Live: `http://` request returns 301 to `https://` (checked 2026-11-12); `Strict-Transport-Security: max-age=3600`; Render deploy log 2026-11-09T09:06:26Z "TLS is active: TLSv1.3; cipher: TLS_AES_256_GCM_SHA384" (`verify_postgres_tls`). Unit: `VerifyPostgresTlsCommandTests` (3), `GmailAPIEmailBackendTests.test_sends_email_through_gmail_https_api` | Passed live; unit tests mock the connection |
| TC-Sec-02 | BOOK-SR-002 | Integration | Passwords stored as salted PBKDF2/Argon2 hashes, never plaintext | `RegistrationIntegrationTests.test_registration_stores_verifiable_hash_not_plaintext`, `SecurityRequestIntegrationTests.test_registered_passwords_are_verifiable_salted_hashes` | Passed |
| TC-Sec-03 | BOOK-SR-003 | System | No card data stored; payment tokenised by the gateway | none (mock gateway, R-002) | **Not verified** |
| TC-Sec-04 | BOOK-SR-004 | Integration | Server-side RBAC: buyers cannot use seller/admin actions; users cannot touch others' resources | `SessionAccessIntegrationTests.test_anonymous_cart_access_redirects_to_login`, `SecurityRequestIntegrationTests.test_seller_cannot_add_or_remove_buyer_wishlist_item`, `SellerEditListingTests.test_seller_cannot_edit_another_sellers_listing` (50 tests map to SR-004) | Passed |
| TC-Sec-05 | BOOK-SR-005 | Integration | SQL-like input is treated literally; HTML in search text and book titles is escaped; CSRF enforced on login/logout/wishlist | `SecurityRequestIntegrationTests.test_sql_like_search_is_literal_and_does_not_broaden_results`, `.test_search_reflection_escapes_html_attribute_payload`, `.test_stored_book_title_is_escaped_in_catalogue_and_detail`; `SessionAccessIntegrationTests.test_login_post_without_csrf_token_is_rejected` | Passed. No penetration/fuzz test has been run (Test Plan §5.1 still lists one) |

## C. Summary against the Test Plan's exit criteria

| Exit criterion | State |
|---|---|
| All planned test cases executed | **Not yet.** All 20 functional cases have a recorded result. Of the 12 non-functional/security cases, 7 have results (TC-Perf-03, Avail-01, Cov-01, Sec-01, Sec-02, Sec-04, Sec-05), 1 is partial (TC-Perf-01) and 4 have none (TC-Perf-02, UX-01, Ops-02, Sec-03) |
| Critical defects resolved or accepted | The four defects found on 2026-11-03 are fixed or revised (R-001). BOOK-NF-002 / the 250-user 503s remain **open** |
| High-priority FRs verified | Automated evidence for F-001 to F-020 (294 passing tests); F-010 is against the mock only |
| Coverage and performance evidence collected | Coverage yes; performance partial (see TC-Perf-01/02) |
| RTM updated with results | `docs/test-reports/traceability.csv` (generated); not yet merged into the SRS RTM |
