# System Validation Report

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

## Execution totals

| Population | Result | Meaning |
|---|---|---|
| Final automated suite | 294 Passed: 18 Unit / 276 Integration | Source 92247d31739eed30e0d769865869869b384a2ba6 |
| Case register | 373 rows: 368 Passed / 2 Failed / 3 Not run | Distinct case definitions; manual subchecks and repeated runs are not added as new case totals |
| Historical system/operational checkpoints | 70 Passed across dates/builds | 64 user manual/tool-assisted, 4 automated public observations, 2 workflow checkpoints |
| Later manual accessibility components | 24 keyboard/zoom/reflow passes plus form/contrast/table reports | Components of the scoped assessment; not 24 extra independent case-register rows |
| Mapped requirements | 31 reviewed; 20 functional requirements | At least 10 mapped case entries per functional requirement; mapping count is not proof that every criterion Passed |

## Work items

| Item | Scope | Execution status | What was tested / limit |
|---|---|---|---|
| OBP-41 | Authentication/account management | Scoped execution complete | Registration/login/logout/protected access, lockout/recovery, reset expiry and real reset mail. Username/session revision retained. |
| OBP-42 | Catalogue/search | Scoped execution complete | Catalogue/search/filter/pagination/detail samples; seller/cover fixes; cache integration tests and separate load evidence. |
| OBP-43 | Cart/checkout | Scoped execution complete | Cart and mock checkout functional checks; twenty completed checkouts passed normal-load timing. No real gateway payment claimed. |
| OBP-44 | Orders/tracking | Scoped execution complete | Order history/details, state tracking, cancellation and return samples; mock-order scope retained. |
| OBP-45 | Seller/admin management | Scoped execution complete | Listing/approval/admin scenarios and role restrictions; seller decision notifications remain unimplemented per D-07. |
| OBP-46 | Reviews/wishlist/notifications | Scoped execution complete | Review/wishlist samples; order-status emails received with correct details. Paid-purchase-only review enforcement not established. |
| OBP-47 | Security | Scoped execution complete with observations | Password hashing, sessions, role/protected access, TLS/CSP/HSTS and recorded scans. Broad HTTPS image-source CSP observation and D-08 request-throttling gap retained. |
| OBP-48 | Non-functional requirements | Scoped execution complete with findings/untested targets | 250-user timing Failed; breadcrumb unresolved; 500/monthly Not tested; full production RPO/RTO unverified. |
| OBP-49 | End-to-end/regression | Hybrid execution complete | Four final historical browser checkpoints plus final 294-test regression. No fresh all-feature manual run on final SHA claimed. |

## Non-functional outcomes

| Requirement | Outcome |
|---|---|
| BOOK-NF-001 | Passed declared normal-load samples: historical catalogue/search p90 0.136/0.142 s; checkout run 43180348416 p90 0.1911 s, 20/20 correct during 10 browsing VUs. Distinct builds/boundaries retained. |
| BOOK-NF-002 | 250-user timing Failed; 100-user sample Passed; 500 users Not tested per revised execution scope. Original 500 target not demonstrated. |
| BOOK-NF-003 | Monthly availability Not tested per user scope decision; no 99.5% full-month claim. |
| BOOK-NF-004 | Executed sampled audit with unresolved admin breadcrumb finding. Manual keyboard/zoom/form/contrast/table follow-up recorded; full conformance and screen-reader speech not established. |
| BOOK-NF-005 | Final CI 43241415099: overall statements 1183/1288=91.85%; branches 247/294=84.01%; defined 20-file core 1013/1093=92.68%, exceeds original 70% target. |
| BOOK-NF-006 | Twice-daily cron published. Fresh backup/temp restore43243243463 Passed; isolated recovery 43243646709 exact 22 tables/258 rows, usable 2.675 s. Historical >24-hour gap and full production RPO/RTO remain unverified. |

## New deployed evidence

- Checkout run 43180348416: 20/20 distinct correct mock orders #9–#28; QA Python Advanced quantity 1 at INR 450.00; p90 191.1 ms, maximum 221.3 ms. Ten browsing VUs sustained for 300.568 s; 1,524/1,524 browsing requests HTTP 200. Timing is POST navigation to loaded confirmation; setup and later detail verification excluded.
- Accessibility run 43230895650: all 34 page/viewport samples completed. One `link-in-text-block` breadcrumb finding affecting three admin order-edit links repeats at desktop/mobile. User retained it unresolved. Original 13 incomplete rule occurrences remain preserved; manual keyboard/zoom/form/contrast/table follow-up is recorded separately. Ratios, exact roles and screen-reader speech were not supplied, so no full WCAG pass is claimed.
- Current backup run 43243243463 and isolated recovery run 43243646709 Passed. Recovery matched 22 tables/258 rows; static assets, health and seven HTTP checks Passed; restore-to-usable 2.675 s, probe 15.056 s. The separate backup ZIP was not inspected. The rehearsal made its own fresh snapshot and restored only to a disposable database; full production outage timing is not established.

## Functional, security and historical qualifications

The four final OBP-49 browser checkpoints retain source afdb5b14 and their recorded context: Order #6 Delivered/details correct, Order #7 created Pending and visible, Order #7 cancellation persisted, and logout protected the cart. The user clarified Order #7 as QA Python Advanced, quantity 1, total `1`; currency/unit-price breakdown were not supplied and are not replaced with a later fixture price.

User-reported real reset mail arrived in the same displayed minute, reset/new login succeeded and the original link became unusable after use. Confirmed/Shipped/Delivered emails for Order #6 each arrived in about five seconds with correct details; three observations are not a delivery percentile.

Historical security evidence includes hashed password storage, protected session-cookie settings, role checks, sanitized log review, TLS/header checks and dependency/static/dynamic scans. Startup output reports PostgreSQL TLS 1.3; CSP/HSTS fixes and live email evidence retain their original builds. ZAP/Bandit findings are triaged rather than reported as zero raw alerts. Broad HTTPS image-source CSP remains an observation. Mock payment initiates Pending records only: no real charge, gateway tokenization or paid-purchase-only review enforcement is established.

The registration error reference is present in the supplied live screenshot; target existence is user-reported. A separate local missing-target reproduction is retained as local evidence, not a confirmed deployed defect. Speech behavior is untested.

## Disposition

The revised execution plan is complete with the recorded exceptions. This does not satisfy every original SRS acceptance criterion. The 500-user and full-month tests are intentionally unexecuted; 250-user timing and the breadcrumb finding remain Failed. Strict historical production RPO and full production outage RTO remain Not verified. Jira changes and publication are performed by the user.

## Developer-documented implementation gaps

The reconciled deviation register retains two additional acceptance limits reported by the developer: seller approval/rejection notifications are unimplemented (D-07), and application-level login/checkout throttling is unimplemented (D-08). Approval/visibility tests and account lockout do not establish those separate criteria. These are documented implementation gaps, not new deployed findings independently executed by this documentation update. Outstanding decision statuses are retained.
