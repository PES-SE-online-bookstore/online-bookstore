# OBP-48 current disposition and remaining work

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

**Status: Revised-scope QA execution complete with findings; publication pending.** The user revised the execution scope: no 500-user run and no monthly availability measurement are planned for this closeout. Original targets remain traceable; neither is reported Passed.

| Requirement | What is complete | Remaining disposition/work |
|---|---|---|
| BOOK-NF-001 response time | Historical normal-load catalogue/search browser samples Passed. Completed mock checkout Passed in run 43180348416: 20 correct orders, p90 191.1 ms, slowest 221.3 ms, ten browsing VUs sustained for 300.568 s | Recorded in final workbook/reports; each execution retains its own build and measurement scope |
| BOOK-NF-002 capacity | 100-user sample Passed; latest 250-user sample Failed the three-second p90 threshold; failed timing evidence retained | 500 users: Not tested. No further load testing planned under the user's revised scope. Do not relabel 250 users Passed |
| BOOK-NF-003 monthly availability | Point-in-time health checks only | Full-month availability: Not tested. Excluded from further execution in this closeout; original 99.5% target is not demonstrated |
| BOOK-NF-004 accessibility | Authenticated run 43230895650 completed all 34 samples: one admin breadcrumb rule/page finding repeated at two widths; 13 incomplete rule occurrences require review. Prior historical samples retained | Scoped follow-up recorded: 24 keyboard/zoom/reflow passes, registration checks, no-issue Firefox contrast sweeps and satisfactory admin table checks, all with source limits. Breadcrumb remains unresolved; screen-reader speech/full conformance not established. Proceed to backup/recovery |
| BOOK-NF-005 core coverage | Verified 294-test CI: statements 91.85%, branches 84.01%, defined 20-file core statements 92.68% | Final CI 43241415099 independently verified; same91.85%/84.01%/92.68% totals and 20-file core scope |
| BOOK-NF-006 backup/recovery | Twice-daily schedule published. Fresh backup/temporary restore run 43243243463 Passed. Current-build isolated recovery run 43243646709 Passed: 22 tables/258 rows, 2.675 s restore-to-usable | Scoped checks complete. Historical >24h gap and unverified strict historical RPO/full production outage RTO remain; no original-target all-Passed claim |

The new checkout execution is preserved in [its review](Runs/CHECKOUT-GHA-43180348416-1/Review.html). Final workbook/reports now reflect373 rows:368 Passed,2 Failed,3 Not run. Older snapshots remain historical evidence. No historical result or missing execution fact is overwritten.

## Work sequence

1. Scope decisions and checkout evidence are recorded locally.
2. Authenticated accessibility scan completed; see the [review](Runs/A11Y-GHA-43230895650-1/Review.html). The user chose to retain the breadcrumb finding unresolved; no unchanged-build rerun is planned.
3. Scoped manual accessibility follow-up complete with evidence limits; see the [assessment checkpoint](Runs/A11Y-GHA-43230895650-1/Scoped_Assessment_Checkpoint.html). Retain the unresolved breadcrumb and unverified criteria; no full conformance pass.
4. Current-build backup/recovery review complete within its stated isolated scope; see [the evidence](Runs/RECOVERY-43243646709/Review.html). Preserve historical cadence and production-wide recovery limits.
5. Main CI run 43241415099 and its artifact are verified;294 Passed, statements 91.85%, branches 84.01%, defined core 92.68%. No further unchanged live execution is planned.
6. Case results, traceability, plans, findings, summary and four reports refreshed locally.
7. Validate the selected deliverables packet; user performs all commits, pushes and Jira publication.

The scope decision is [recorded separately](../02_Plan_and_Scope/OBP48_Closeout_Scope_2026-11-12.json). The earlier failed capacity and backup-cadence findings are preserved. No new live execution occurred while updating this guide.
