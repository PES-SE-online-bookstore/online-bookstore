# Hosted browsing load review — run 42964208887

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

11 November 2026, 05:13–05:24 UTC (10:43–10:54 IST). The workflow stopped at its request reconciliation gate. All 8,552 recorded requests returned HTTP 200 with no recorded request failures. Two additional started requests have no completion record, so the 100-user stage remains inconclusive.

| Active virtual users | Steady sample | Catalogue HTTP p90 | Search HTTP p90 | Result |
|---|---|---|---|---|
| 1 | 60 seconds | 0.127 s | 0.113 s | Passed scoped browsing stage |
| 10 | 300 seconds | 0.120 s | 0.128 s | Passed scoped browsing stage |
| 50 | 120 seconds | 0.301 s | 0.294 s | Passed scoped browsing stage |
| 100 | 120 seconds | 2.136 s | 2.120 s | Inconclusive: 3,876 started / 3,874 completed |
| 250 and 500 | Not run | — | — | Higher stages skipped |

The independent Chromium browser ran during the 10-VU steady sample: 20 catalogue and 20 search navigations, correct HTTP 200 pages, p90 page loads **0.136 s** and **0.142 s**. All 40 measured page loads were below 3 seconds. These complete cases OBP48-PERF-001/002 for the declared anonymous normal-load profile. BOOK-NF-001 remains partial because authenticated checkout timing is unverified.

## Why this workflow was red

The old controller stopped Locust users before explicitly waiting for every active request to finish. The final stage had two unmatched started requests. Their outcomes are unknown: the artifact does not prove timeouts, application errors or successful completion. No application defect is established from this discrepancy. Completed responses alone cannot turn that stage into a Pass.

The prepared controller now prevents new requests at the stage boundary and waits up to 35 seconds for active requests before shutting down users. It still fails on unmatched counts, HTTP errors and the unchanged timing gates. A localhost fixture with ten deliberately delayed requests passed with all counts reconciled; zero public calls were made by that check. This validates the fix locally and does not supply a replacement hosted capacity result.

Reported deployed SHA and harness SHA: `26f62e6eca81feee7ef5736568ec24f8328352dd`. The deployed SHA is operator supplied, not independently exposed by the app. Render log observations for this hosted window have not been supplied. Earlier no-error observations apply only to local LOAD-001.

The profile exercises anonymous catalogue/search HTML GETs. The 10-user stage adds one measurement browser. It excludes authenticated checkout and cannot establish whole-system 500-user capacity. Latency also increased at 100 users compared with the one-user baseline; staying below a three-second gate does not demonstrate zero degradation.

Original ZIP, summary, request CSV, browser results and operator-pasted log are preserved unchanged alongside this review. Publish the corrected controller and start a new workflow run on its new commit. Rerunning an old revision would retain the old generator.
