# Developer handoff — 250-user browsing failure

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Finding draft: catalogue/search return HTTP 503 under the 250-user browsing stage. BOOK-NF-002 / OBP-48.

Evidence: GitHub Actions run https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/42969189618. Reported deployment and harness SHA `5752e3e02e2507be060d480c411c14f4dd70e5a9`.

Workload: anonymous GET /books/ and /books/?q=QA, random task weighting 3:2, independent VU sessions, think time 1–3 seconds. Staged 1/10/50/100/250 users. The 250 stage spawns ten users per second, then ten seconds warm-up, then a planned 120-second hold. It stopped early on a 503. No real order/payment/account mutations were performed.

Expected: no service errors during the target workload; browsing p90 <=3 seconds. The overall stated capacity target remains 500 concurrent users.

Actual: 1/10/50/100-user browsing stages passed their gates. At 250 users, three catalogue and three search requests returned 503 at 06:11:01.998–06:11:02.133 UTC on 11 November. Successful-request p90 in the short aborted steady sample was approximately eight seconds. All 9,606 started requests were accounted for; 500 users were not run. The generator used at most sampled 9% CPU / 91.52 MiB RSS. User reports no relevant Render log errors visible.

Investigate before another public stress run:

1. Correlate web-service events, CPU/memory and database connections/metrics for 06:10:25–06:11:10 UTC, including proxy/platform errors not shown in application logs.
2. Record the actual running server command, worker/concurrency settings, service resources and database limits. Repository defaults alone do not prove the live configuration.
3. Check query counts/durations for catalogue/search and whether requests queue or exhaust any resource. Retain the measured cause; do not assume the free plan or a specific component caused the 503s.
4. If current logs cannot identify the source, prepare focused diagnostic logging/metrics. Capture sanitized 503 response headers and a safe response classification in the next relevant run; no credentials, cookies or full response bodies.
5. Return the diagnosis, changed configuration/commit if any, actual deployed SHA, and a proposed targeted verification. Leave the thresholds and historical failure unchanged.

This is a local finding draft for the QA lead to publish if desired. It does not claim a known root cause or an exact capacity ceiling.
