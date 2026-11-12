# Targeted cache retest — run 43035954975

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

11 November 2026, 14:10:55–14:14:29 UTC (19:40:55–19:44:29 IST). Reported deployed SHA and harness SHA: `aa36272e424489724153b8cdd89c1ae25b4a8e13`. Runtime identity is operator supplied.

**The controller correctly stopped on the 250-user latency gate. No HTTP error or request-accounting failure occurred.**

| Stage | Recorded requests, all phases | Steady requests | Catalogue p90 | Search p90 | Outcome |
|---|---|---|---|---|---|
| 100 VUs | 6,249 | 5,497 | 0.332 s | 0.321 s | Passed 120-second steady sample |
| 250 VUs | 3,136 | 1,426 | 3.807 s | 3.792 s | Failed sustained three-second gate; early stop after about 30 of 120 seconds |
| 500 VUs | 0 | 0 | Not measured | Not measured | Not run; outside targeted profile |

All 9,385 started requests completed and returned HTTP 200. At the 250-user cutoff, 143 active requests drained successfully in 2.894 seconds. Peak sampled generator CPU was 11%, RSS 96.34 MiB; no generator resource stop threshold was reached. These are generator measurements, not Render resource measurements.

## Cache and timing diagnostics

| Steady stage / endpoint | Cache HIT / successful responses | HIT share | Data p90 | Instrumented app p90 | Client-minus-instrumented-app p90 |
|---|---|---|---|---|---|
| 100 / catalogue | 3,253 / 3,259 | 99.82% | 0.5 ms | 15.5 ms | 320.589 ms |
| 100 / search | 2,232 / 2,238 | 99.73% | 0.5 ms | 19.0 ms | 306.702 ms |
| 250 / catalogue | 848 / 850 | 99.76% | 0.5 ms | 79.4 ms | 3,778.756 ms |
| 250 / search | 575 / 576 | 99.83% | 0.5 ms | 85.6 ms | 3,783.239 ms |

Every successful response had the required diagnostics. HIT shares use successful-response denominators; there were no failed responses. The residual is computed per request before its p90 is taken. It includes network, proxy, possible queueing and other uninstrumented work; it is not a direct queue-time measurement. Percentiles of separate metrics must not be subtracted or added as though they describe the same request.

Only 290/850 catalogue and 188/576 search requests in the 250-user steady sample completed within three seconds. HTTP 200 alone does not satisfy the timing gate. The 250-user sample was aborted and does not establish a successful two-minute hold or an exact maximum capacity.

## Comparison and disposition

Before caching, run 42969189618's 100-user catalogue/search p90 was 2.205s/2.204s. This retest measured 0.332s/0.321s, approximately 84.9%/85.5% lower. These are observed results across two deployments/runs, not a controlled proof that every difference came from caching. The previous six 503s were not reproduced in this sample; their permanent elimination is not established.

The cache is active and supports materially faster measured 100-user browsing. The tested deployment still misses the 250-user three-second latency gate. BOOK-NF-002 remains unmet/unverified at its original 500-user target. The agreed single optimisation/retest cycle is complete with a failed capacity outcome. Preserve the finding and stop further public stress reruns or tuning within this cycle. A future deployment/optimization can be separately verified.

BOOK-NF-001 still lacks authenticated checkout timing. Monthly availability, full applicable accessibility and operational backup/RPO evidence remain separate gaps. OBP-48 is still In Progress; earlier passing recovery and scoped functional/security evidence remain valid within their stated build/scope limits.

Render logs/CPU/memory for this retest have not yet been supplied. Earlier observations must not be reused for this window. Original ZIP, JSON, CSV and pasted workflow log are preserved unchanged. No new Jira bug, application/workflow change, deployment or public load run was made during this review.
