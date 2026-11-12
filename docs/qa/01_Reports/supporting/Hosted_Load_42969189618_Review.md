# Hosted browsing load review — run 42969189618

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

11 November 2026, 05:58:49–06:11:09 UTC (11:28:49–11:41:09 IST). Reported deployed and harness SHA: `5752e3e02e2507be060d480c411c14f4dd70e5a9`. Deployment identity is operator supplied.

**The 250-user stage failed with six HTTP 503 responses. The earlier shutdown-accounting problem is resolved in this run.**

| Active VUs | Catalogue HTTP p90 | Search HTTP p90 | Outcome |
|---|---|---|---|
| 1 | 0.089 s | 0.110 s | Passed 60-second steady sample |
| 10 | 0.107 s | 0.114 s | Passed 300-second steady sample |
| 50 | 0.287 s | 0.288 s | Passed 120-second steady sample |
| 100 | 2.205 s | 2.204 s | Passed 120-second steady sample |
| 250 | 7.976 s | 7.949 s | Failed, early abort after about two seconds of steady-stage controller time |
| 500 | Not measured | Not measured | Not run |

The 250-user p90 values are diagnostic statistics for successful requests in an aborted, short stage. They do not describe a completed two-minute steady sample. Phases are captured at request initiation; the controller waits for in-flight requests after stopping new work. At 10 users there were three successful HTTP requests above three seconds, although per-endpoint p90 passed. At 100 users latency was materially higher than the one-user baseline, despite remaining within the three-second gate.

## Verified request accounting and failures

- 9,606 started = 9,606 completed. 9,600 returned HTTP 200; six returned HTTP 503.
- All six 503s occurred at 250 active users: three catalogue and three search. Completion timestamps: 06:11:01.998–06:11:02.133 UTC (11:41:01.998–11:41:02.133 IST).
- At the 100-user cutoff, 60 active requests drained successfully in 2.476 seconds.
- At the 250-user cutoff, 191 active requests drained successfully in 7.693 seconds. No requests remain unaccounted for.
- Peak sampled generator CPU was 9%, memory 91.52 MiB. No sampled generator saturation threshold was reached. Server resource utilization is not included.

The workflow's nonzero exit correctly reports the failed service/correctness gate. No further controller correction is indicated by this artifact. The service-error origin is unknown because per-error response headers/bodies and server/platform resource data are absent. The operator checked Render logs for 11:40:25–11:41:10 IST and reported none of the requested errors visible. This does not establish that the 503s did not occur or identify their source.

## Normal-load browser evidence

During ten active VUs plus one sequential Chromium browser, 20 catalogue and 20 search page loads passed correctness and the three-second gate. Catalogue p90: 0.1351 s, maximum 0.3432 s. Search p90: 0.1254 s, maximum 0.2334 s. All 40 measured navigations were below three seconds. Original PERF-001/002 Pass evidence remains valid and this run corroborates it.

## Disposition and next action

BOOK-NF-002 is not met by this execution. The public browsing workload failed at 250 users, and 500 users were not tested. Do not report an exact maximum capacity or a successful 500-user test. BOOK-NF-001 remains partial because authenticated checkout timing is unverified. OBP-48 remains In Progress.

Preserve this run and send the accompanying developer handoff for investigation. Check platform metrics/events, actual worker/concurrency configuration and database/query behavior around the failure window. Do not change deployment settings or repeat the unchanged public stress test until there is a diagnostic plan or a relevant fix to verify. Other QA finalization work can continue with this finding recorded.

Original ZIP, summary, request CSV, browser data and pasted workflow log are preserved unchanged in this folder. No Jira issue was published and no new public load test was run while reviewing the artifact.
