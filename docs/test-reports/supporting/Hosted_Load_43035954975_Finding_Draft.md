# Capacity finding draft — latency gate missed at 250 users

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Related requirement/work item: BOOK-NF-002 / OBP-48. This is a local draft; no Jira issue was created.

Build: user-reported deployed/harness commit `aa36272e424489724153b8cdd89c1ae25b4a8e13`, including the catalogue-data cache. Run: https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43035954975.

Workload: anonymous GET /books/ and /books/?q=QA, 3:2 random weighting, 1–3 second think time, 10 users/second ramp, 10-second warm-up, planned 120-second steady stages at 100 then 250 VUs. The browsing gate is p90 <=3 seconds per endpoint, with zero request errors and full request reconciliation.

Actual: 100-user stage Passed. At 250 users the sustained latency stop fired after about 30 seconds; catalogue/search p90 was 3.807s/3.792s. Cache HIT shares were 99.76%/99.83%; all 9,385 recorded responses across the run were HTTP 200 and all started requests were accounted for. 500 users were not run. No exact maximum capacity or full-system result is established.

Disposition: retain failed 250-user timing acceptance and original 500-user target as unmet/unverified. The agreed optimisation cycle is finished; no further unchanged public rerun is proposed. Continue remaining NFR evidence and final documentation. Document any later scope/environment change explicitly; it is not a passing result against the original target.

Diagnostics support active caching and a large 100-user timing improvement. They do not independently identify the remaining external/instrumentation-residual delay as CPU throttling, queueing or a particular proxy behavior. Add the operator's Render observations when supplied.
