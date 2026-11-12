# Deviations from the submitted SRS, SAD and Test Plan

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated evidence is CI [43241415099](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099), source `92247d31739eed30e0d769865869869b384a2ba6`. Later checkout, accessibility and recovery evidence is linked in the QA packet with its own tested build. The developer's twelve deviation IDs are retained below.

**Decision status.** Only R-001 and R-002 have a recorded decision (QA Lead
Abdullah Faruqui and Test Engineer Deepthi A E, 2026-11-09; see
`qa/REQUIREMENT_REVISIONS.md`). The remaining implementation-deviation decisions retain their recorded status. Later user decisions about which tests to execute are listed separately below; they do not approve every implementation deviation.

| # | Document and section | Specified | Implemented | Reason | Decision status |
|---|---|---|---|---|---|
| D-01 | SRS BOOK-F-002; SAD §4.3, Fig. 5 | Login with **email** and password | Login with **username** and password; an email address is rejected as the identifier | The login form and Django authentication use usernames; email stays unique (F-001) and is the password-reset identifier (F-004) | **R-001, decided 2026-11-09** |
| D-02 | SRS BOOK-F-010, BOOK-SR-003, §3.3; SAD §3.5 ADR-003, Fig. 3 | Payment through a Razorpay/Stripe sandbox gateway with tokenised card details | In-process `MockPaymentGateway`; it simulates initiation only. No gateway call, no money moves, no card data collected or stored. (The `razorpay` package is listed in `requirements.txt` but not imported anywhere in the application code.) | Academic scope and time; SRS §2.5 already restricts payments to test mode | **R-002, decided 2026-11-09** |
| D-03 | SAD §3.3, §3.5 ADR-002, §4.3; Test Plan §2, §6 | REST API (`/api/...`) built with Django REST Framework, JWT bearer tokens, standard JSON error format | Server-rendered Django views and templates; browser sessions with CSRF protection. `djangorestframework` is installed but not enabled in `INSTALLED_APPS`. The only JSON endpoint is `/health/` | Simpler to build and test as one Django project; the JSON API was not needed by the web UI | Awaiting team sign-off |
| D-04 | SAD §3.3, §3.4 (EmailClient: "SMTP / API"); Test Plan §6 | SMTP email service | Django email backend `config.email_backends.GmailAPIEmailBackend`, sending over the Gmail **HTTPS API** with OAuth credentials from environment variables | The Render free plan blocks SMTP ports 25/465/587 | Awaiting team sign-off |
| D-05 | SAD §4.1 (order statuses) | PLACED, SHIPPED, DELIVERED (+ cancel/return) | PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED; return requests are a separate record. Status emails are sent for CONFIRMED, SHIPPED and DELIVERED | Finer-grained lifecycle (payment confirmation, processing) | Awaiting team sign-off |
| D-06 | SAD §4.6 and SRS BOOK-F-012 ("Optional shipping API"); Test Plan §11 | Shipping API, or manual status updates (an open decision in the SAD) | No shipping API. Tracking is a status timeline updated by staff; the page states that live courier tracking is unavailable | Resolves the SAD open issue in favour of manual status | Awaiting team sign-off |
| D-07 | SRS AC-BOOK-F-016; SAD §3.4 (NotificationModule: "listing decisions"), Fig. 4 | Seller notified when a listing is approved or rejected | No email or notification is sent to the seller on approve/reject. (Searched `books/admin.py`, `views.py`, `models.py`, `signals.py` for mail or notification code: none.) Status is visible to the seller on "My listings" | Not implemented | Awaiting team decision: implement or accept as a gap |
| D-08 | SAD §3.9 (Denial of service: "request limits") | Request limits on login and checkout | No application-level request throttling. Brute force is limited by the 5-attempt / 15-minute account lockout (F-003); pagination limits catalogue size | Not implemented | Awaiting team decision |
| D-09 | SAD §4.6 and Test Plan §4 | Caching listed as a *future idea* and explicitly out of test scope | A limited **catalogue query-result cache** (30 s, in-process, invalidated on book changes) was added in PR #3 for OBP-48, with 26 automated tests. Rendered pages are not cached | Added to investigate the capacity finding. The 26 cache tests Passed, and a later cache-enabled 100/250-user retest was executed; correctness is distinct from capacity acceptance. | Documented in `qa/OBP48_CATALOGUE_CACHE.md`; awaiting team sign-off |
| D-10 | Test Plan §6; SAD §3.6 | Jenkins CI/CD, Docker, SonarQube, JWT tooling | GitHub Actions for Django CI, backup/temporary restore, controlled browsing load, completed checkout, authenticated accessibility and isolated recovery; Render hosting. No Dockerfile/SonarQube configuration is claimed. | Implemented project tooling differs from the submitted design. Current backup cron is twice daily; original workflow name remains Daily Database Backup. | Awaiting team sign-off |
| D-11 | SRS BOOK-NF-002 (500 concurrent users) | 500 concurrent users without degradation | Original 500-user target not demonstrated. Latest cache-enabled run 43035954975: 100-user stage Passed; 250-user p90 3806.835/3792.473 ms exceeded 3000 ms; the hold stopped early. All 9385 requests returned HTTP 200. Earlier six HTTP 503 responses remain historical evidence; exact response-origin/root-cause conclusions are not established by this artifact. | Measured capacity limit under the declared workload. User ended further capacity execution after the existing 250-user tests. | Open failed timing finding. 500 users Not tested per user execution scope; original SRS target is not claimed met. |
| D-12 | SRS BOOK-NF-005 (70% of *core business logic*) | Coverage target on core modules | Final CI: 1183/1288 statements=91.85%; 247/294 branches=84.01%. Explicit QA core scope: 20 accounts/books/cart/orders business files, 1013/1093 statements=92.68%. Exact files are in `qa/01_Reports/supporting/Core_Coverage_Scope.json`. | QA defined and retained the same 20-file scope; no uncovered file was removed to improve the metric. | QA measurement definition and results recorded. The scoped 92.68% exceeds the 70% target; this does not approve unrelated deviations. |

## Defects found and fixed during QA (not deviations)

| Finding | Requirement | Fix | Evidence |
|---|---|---|---|
| Reset link usable after 30 minutes (Django's default timeout is 3 days) | BOOK-F-004 | `PASSWORD_RESET_TIMEOUT = 1800` | `qa/history/2026-11-03_run_29049b0.md` |
| Seller not shown on book detail | BOOK-F-007 | "Sold by" line added | same |
| Cover image missing from catalogue cards | BOOK-F-005 | Cover image or placeholder added | same |

The historical failed run (253 tests, 4 failures) is preserved unchanged in
`qa/history/`.

## Later execution-scope decisions and findings

- The user ended further capacity execution after the existing 250-user tests. Record 500 users as **Not tested**, and keep the actual 250-user timing result **Failed**.
- Full-month availability was excluded from further execution and remains **Not tested**. No 99.5% monthly result is inferred from health checks.
- The user retained the admin order breadcrumb accessibility finding **unresolved**. The same rule/page finding appears at two viewport widths; it is not two separate bugs.
- These are recorded QA execution/disposition decisions, not blanket approval of D-03 through D-10 or changes to every original SRS criterion.

## Known limits and current evidence

- Mock payment does not verify a real gateway, tokenization or genuinely confirmed payment (D-02).
- Seller approval/rejection notification remains the developer-documented unimplemented gap (D-07). Passing approval/visibility tests do not establish that notification acceptance criterion.
- Application request throttling remains the developer-documented gap (D-08). Account lockout is separate evidence.
- Real reset and Confirmed/Shipped/Delivered order emails have user-reported delivery evidence. Automated Gmail API tests still mock HTTP; no delivery percentile is claimed.
- Checkout run 43180348416: twenty correct mock orders, p90 191.1 ms during ten browsing VUs. Build attribution remains distinct from final CI.
- Accessibility run 43230895650 completed 34 samples. Breadcrumb finding unresolved; original 13 incomplete rule occurrences and manual follow-up remain recorded. No full WCAG conformance or screen-reader speech result is claimed.
- Backup schedule is published twice daily. Fresh backup/temporary restore run 43243243463 and isolated recovery run 43243646709 Passed; recovery exactly matched 22 tables/258 rows and reached a usable flow in 2.675 seconds. Historical >24-hour backup spacing and full production RPO/RTO remain unverified. No database dump belongs in this documentation packet.

See [the QA evidence index](qa/QA_Index.md) and [final findings](qa/01_Reports/Open_Items_and_History.md). Original PDFs remain unchanged.
