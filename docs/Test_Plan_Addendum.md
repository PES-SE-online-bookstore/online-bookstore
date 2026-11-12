# Test Plan addendum

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The submitted Test Plan PDF remains unchanged. This addendum retains the developer's 32 requirement-level scenario summaries and reconciles them with the detailed final QA register.

Final automated baseline: [CI 43241415099](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099), source `92247d31739eed30e0d769865869869b384a2ba6`: **294 Passed, 18 Unit / 276 Integration, zero failures/errors/skips**. Statement coverage 91.85%, branch coverage 84.01%, defined core statement coverage 92.68%.

The detailed register is [the Cases/RTM workbook](qa/03_Cases_and_RTM/QA_Test_Cases_and_RTM_Draft.xlsx): **373 records, 368 Passed, two Failed, three Not run; 31 requirement mappings**. The 32 rows below summarize requirements/scenarios; they are not a replacement for the 373 detailed records or 294 executable tests. The [crosswalk](qa/03_Cases_and_RTM/Scenario_Summary_Crosswalk.md) links them to the detailed register.

The course requests manual execution; actual project execution is the user's hybrid method. Automated results keep their true level/method. No claim is made that all records were manually executed.

## A. Revisions to Test Plan sections

| Section | Submitted text | Revised text |
|---|---|---|
| 4 Features Not to be Tested | "advanced search/caching ... unless later included" | A limited catalogue query-result cache **is** included in the build (OBP-48) and is tested (cases TC-Perf-03 and `books.test_catalogue_cache`). Two-factor login and wishlist price alerts remain out of scope |
| 6 Test Environment: software | "JWT authentication", "Django REST Framework" | Server-rendered Django with session authentication and CSRF protection (see Deviations D-03) |
| 6 Test Environment: tools | "Jenkins for CI/CD; Docker; SonarQube" | GitHub Actions (Django CI on PostgreSQL, twice-daily backup, controlled browsing load, completed checkout, authenticated accessibility and isolated recovery); `coverage.py` with the QA reporting tool in `qa/`; Render hosting |
| 6 Test Environment: external services | "Razorpay or Stripe sandbox, SMTP/test email service" | Mock payment gateway (R-002); Gmail HTTPS API for email |
| 11 Assumptions | "Payment testing will use a sandbox/test gateway" | Payment testing uses the in-process mock gateway; gateway acceptance is not verified (R-002) |
| 13 Traceability | "final RTM will be updated" | All 31 requirements are reviewed in the detailed Cases/RTM workbook and [detailed traceability JSON](qa/03_Cases_and_RTM/Traceability_Matrix_Final.json). Raw automated-only mapping remains in `test-reports/traceability.csv`; mapping is not full acceptance. |

## B. Test-case table

Levels follow the Test Plan (Unit / Integration / System). Automated outcomes use final CI 43241415099. Deployed/manual/operational results identify their distinct run and boundary. Passed implementation tests do not establish unimplemented acceptance criteria.

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
| TC-Admin-01 | BOOK-F-016 | Integration | Admin approves or rejects; only approved listings are public; rejected listings are hidden | `AdminListingApprovalTests.test_admin_can_approve_pending_listing`, `.test_rejected_listing_does_not_appear_in_public_catalogue` | Approval/visibility checks Passed. Seller decision notification is unimplemented per developer D-07; full notification criterion not claimed Passed. |
| TC-Admin-02 | BOOK-F-017 | Integration | Deactivated listings and accounts are inaccessible to buyers | `AdminInventoryManagementTests` (class), `LoginIntegrationTests.test_inactive_account_cannot_log_in` | Passed |
| TC-Rev-01 | BOOK-F-018 | Integration | Only a buyer who purchased the book can review; rating 1–5 enforced; average rating shown | `ReviewRolePermissionTests.test_buyer_with_purchase_can_submit_review`, `BookReviewTests.test_invalid_rating_is_rejected` | Passed within ordered-item/mock-payment scope. Verified-paid-purchase-only enforcement is not established. |
| TC-Rev-02 | BOOK-F-019 | Integration | Wishlist add/remove is POST-only, CSRF-protected, per buyer and idempotent | `SecurityRequestIntegrationTests.test_valid_csrf_wishlist_add_is_idempotent`, `.test_other_buyer_cannot_view_or_remove_saved_item` | Passed |
| TC-Rev-03 | BOOK-F-020 | Integration + Unit | Emails on CONFIRMED, SHIPPED, DELIVERED; none on cancel; a mail failure never blocks the status change; Gmail API backend sends over HTTPS | `OrderEmailNotificationTests.test_confirmed_status_sends_email`, `.test_email_failure_does_not_prevent_status_update`; `GmailAPIEmailBackendTests` (5, mocked HTTP) | Automated checks Passed. User reports correct real Confirmed/Shipped/Delivered messages for Order #6, each arriving in about five seconds. These are samples, not a delivery percentile. |

### Non-functional and security requirements

| TC ID | Requirement | Level | Scenario and expected result | Evidence | Result |
|---|---|---|---|---|---|
| TC-Perf-01 | BOOK-NF-001 | System | Catalogue/search p90 <=3 s and completed mock-checkout p90 <=5 s under their declared normal-load samples | Historical normal-load browser evidence run 42964208887; completed checkout run 43180348416; see `qa/06_NFR_and_Recovery/Runs/`. | Passed those declared samples: catalogue/search p90 0.136/0.142 s; checkout 20/20 correct, p90 0.1911 s during ten browsing VUs. Build/timing boundaries retained. Separate 250-user capacity failure is not a normal-load pass. |
| TC-Perf-02 | BOOK-NF-002 | System | 500 concurrent users without errors | Latest cache-enabled load run 43035954975; detailed case OBP48-LOAD-002. | 500 users Not tested per user execution scope. Latest 250-user timing Failed at 3.807/3.792 s against 3 s; 100-user sample Passed. Earlier 503 evidence preserved separately. |
| TC-Perf-03 | BOOK-NF-002 (cache correctness support; related BOOK-NF-001) | Integration | Catalogue cache: expiry, invalidation, query and session separation, CSP nonce per response, diagnostics headers | `books/test_catalogue_cache.py` (26 tests) | 26 cache Integration tests Passed. Correctness support does not establish concurrent-user capacity. |
| TC-Avail-01 | BOOK-NF-003 | Integration | `/health/` returns 200 when the database is reachable and 503 when it is not | `HealthCheckTests.test_health_check_returns_200_when_database_is_available`, `.test_health_check_returns_503_when_database_fails` | Health integration checks Passed. Full-month 99.5% availability Not tested per user scope decision. |
| TC-UX-01 | BOOK-NF-004 | System | Responsive layout and WCAG 2.1 AA audit | Authenticated scan 43230895650 and manual follow-up in `qa/06_NFR_and_Recovery/Runs/A11Y-GHA-43230895650-1/`. | Executed sampled audit: 34/34 scans; unresolved admin breadcrumb finding; 24 manual keyboard/zoom/reflow passes plus form/contrast/table reports. Original incomplete checks/evidence limits retained; full conformance and speech not established. |
| TC-Cov-01 | BOOK-NF-005 | CI | Coverage of core logic ≥ 70% | [Code Coverage Report](test-reports/Code_Coverage_Report.md), [Branch Coverage Report](test-reports/Branch_Coverage_Report.md) | Defined 20-file core: 1013/1093=92.68%, exceeds 70%. Overall statements 91.85%, branches 84.01%. Scope listed in Core_Coverage_Scope.json. |
| TC-Ops-02 | BOOK-NF-006 | System | Daily backup; restore meets RPO 24 h / RTO 4 h | Published schedule plus backup 43243243463 and isolated recovery 43243646709, source 92247d3; summaries under `qa/06_NFR_and_Recovery/Runs/`. | Fresh backup/temp restore Passed. Isolated recovery matched 22 tables/258 rows, usable 2.675 s. Twice-daily schedule published. Historical >24-hour gap and complete production RPO/RTO remain unverified. |
| TC-Sec-01 | BOOK-SR-001 | System + Unit | Plain HTTP is redirected; HSTS set; database connection encrypted; third-party calls verify certificates | Live: `http://` request returns 301 to `https://` (checked 2026-11-12); `Strict-Transport-Security: max-age=3600`; Render deploy log 2026-11-09T09:06:26Z "TLS is active: TLSv1.3; cipher: TLS_AES_256_GCM_SHA384" (`verify_postgres_tls`). Unit: `VerifyPostgresTlsCommandTests` (3), `GmailAPIEmailBackendTests.test_sends_email_through_gmail_https_api` | Passed live; unit tests mock the connection |
| TC-Sec-02 | BOOK-SR-002 | Integration | Passwords stored as salted PBKDF2/Argon2 hashes, never plaintext | `RegistrationIntegrationTests.test_registration_stores_verifiable_hash_not_plaintext`, `SecurityRequestIntegrationTests.test_registered_passwords_are_verifiable_salted_hashes` | Passed |
| TC-Sec-03 | BOOK-SR-003 | System | No card data stored; payment tokenised by the gateway | none (mock gateway, R-002) | **Not verified** |
| TC-Sec-04 | BOOK-SR-004 | Integration | Server-side RBAC: buyers cannot use seller/admin actions; users cannot touch others' resources | `SessionAccessIntegrationTests.test_anonymous_cart_access_redirects_to_login`, `SecurityRequestIntegrationTests.test_seller_cannot_add_or_remove_buyer_wishlist_item`, `SellerEditListingTests.test_seller_cannot_edit_another_sellers_listing` (50 tests map to SR-004) | Passed |
| TC-Sec-05 | BOOK-SR-005 | Integration | SQL-like input is treated literally; HTML in search text and book titles is escaped; CSRF enforced on login/logout/wishlist | `SecurityRequestIntegrationTests.test_sql_like_search_is_literal_and_does_not_broaden_results`, `.test_search_reflection_escapes_html_attribute_payload`, `.test_stored_book_title_is_escaped_in_catalogue_and_detail`; `SessionAccessIntegrationTests.test_login_post_without_csrf_token_is_rejected` | Mapped integration checks Passed. Scoped security/static/dependency/dynamic-scan evidence is retained in the QA packet; comprehensive penetration/fuzz coverage is not established. |

## C. Exit-criteria assessment

| Exit criterion | Current assessment |
|---|---|
| Original all-planned targets executed | Not met as an all-target statement. Agreed QA execution is complete with retained findings and exclusions; 500-user/monthly and full production RPO cases remain unexecuted/unverified. |
| Critical defects and remaining findings | Historical authentication/catalogue fixes are retained. 250-user timing and admin breadcrumb finding remain Failed/unresolved. Developer implementation gaps D-07/D-08 remain visible. |
| Functional evidence | Final 294-test regression Passed; manual functional evidence retains its own builds. Mock payment, seller notification and paid-purchase-only qualifications remain explicit. |
| Coverage/performance evidence | Final coverage verified; normal-load checkout/catalogue/search samples available. Capacity failure remains separate. |
| Traceability | All 31 requirements reviewed in the detailed workbook/JSON; the 32 summary rows have an explicit crosswalk. Original PDFs not updated by this addendum. |

## D. Evidence/provenance rules

Curated reports in `test-reports/` combine the inspected CI artifact and separately attributed deployed/manual evidence; they are not unchanged autogenerated CI reports. The raw CI CSV/metadata/coverage files are preserved from final run 43241415099. Branch tables display N/A when there are zero branch opportunities. Historical failures, the unresolved breadcrumb and untested targets are retained.

The 32 scenario IDs above and their intent remain the developer's summary catalogue. Exact fixtures, assertions, expected/actual results and source links are in the detailed case register. Counts of scenarios, test cases, automated methods and manual subchecks describe different populations and must not be added together.
