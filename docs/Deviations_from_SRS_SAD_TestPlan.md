# Deviations from the submitted SRS, SAD and Test Plan

Status as of 2026-11-12, `main` at `f6d7d85`. This list was prepared by the
developer from the repository, the three submitted PDFs and the QA results. It
is written so the team can explain each deviation at the demo.

**Decision status.** Only R-001 and R-002 have a recorded decision (QA Lead
Abdullah Faruqui and Test Engineer Deepthi A E, 2026-11-09; see
`qa/REQUIREMENT_REVISIONS.md`). Every other row is *documented, awaiting team
sign-off*: do not present it as already approved.

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
| D-09 | SAD §4.6 and Test Plan §4 | Caching listed as a *future idea* and explicitly out of test scope | A limited **catalogue query-result cache** (30 s, in-process, invalidated on book changes) was added in PR #3 for OBP-48, with 26 automated tests. Rendered pages are not cached | Response to the 250-user load finding | Documented in `qa/OBP48_CATALOGUE_CACHE.md`; awaiting team sign-off |
| D-10 | Test Plan §6; SAD §3.6 | Jenkins CI/CD, Docker, SonarQube, JWT tooling | GitHub Actions (5 workflows: Django CI, daily database backup, controlled browsing load, completed-checkout performance, isolated recovery rehearsal) and Render hosting. No Dockerfile or SonarQube configuration in the repository | Tooling available to the team | Awaiting team sign-off |
| D-11 | SRS BOOK-NF-002 (500 concurrent users) | 500 concurrent users without degradation | **Not met and not yet demonstrated.** On the Render free plan (1 instance, default single gunicorn worker) the 250-user browsing stage returned six HTTP 503s from the platform's routing layer; the 500-user stage was not started. See `qa/OBP48_CATALOGUE_CACHE.md` | Free-tier capacity; root cause of the platform 503s is not proven | Open finding; thresholds unchanged |
| D-12 | SRS BOOK-NF-005 (70% of *core business logic*) | Coverage target on core modules | Measured package-wide: 91.85% line, 84.01% branch (CI run 43174812573). "Core business logic" has not been formally scoped | The scope definition is still to be agreed | Awaiting team decision |

## Defects found and fixed during QA (not deviations)

| Finding | Requirement | Fix | Evidence |
|---|---|---|---|
| Reset link usable after 30 minutes (Django's default timeout is 3 days) | BOOK-F-004 | `PASSWORD_RESET_TIMEOUT = 1800` | `qa/history/2026-11-03_run_29049b0.md` |
| Seller not shown on book detail | BOOK-F-007 | "Sold by" line added | same |
| Cover image missing from catalogue cards | BOOK-F-005 | Cover image or placeholder added | same |

The historical failed run (253 tests, 4 failures) is preserved unchanged in
`qa/history/`.

## Known limits of the evidence

- The mock payment gateway means no gateway acceptance, tokenisation
  (BOOK-SR-003) or payment-confirmation email (BOOK-F-010) has been verified.
- Email delivery was confirmed by one controlled test message on 2026-11-03; the
  automated email tests mock HTTP.
- Accessibility (BOOK-NF-004), monthly availability (BOOK-NF-003) and the daily
  backup/restore targets (BOOK-NF-006) have no result recorded in this
  repository.
