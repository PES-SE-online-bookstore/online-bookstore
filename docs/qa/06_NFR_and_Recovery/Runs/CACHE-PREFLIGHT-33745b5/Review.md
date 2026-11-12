# Cache-build live preflight and targeted test preparation

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

User-reported live revision: `33745b521ffcb3e57c2287c943662c6526582078`. The app does not expose a runtime commit identifier. Hosted CI artifact checksum and all 294 test results were independently verified.

Four sequential public GETs, no form submissions or load generation: health, catalogue twice, and search. All returned HTTP 200. Catalogue MISS then HIT; Server-Timing present; header/body CSP nonces matched and differed across the two catalogue responses. CSP enforcement and HSTS max-age=3600 remained present. These checks support the new live diagnostic behavior, not capacity acceptance or a browser rendering result.

The first health request took 41.833 seconds from this client. Its cause was not isolated, and the delay is retained in the raw JSON. Subsequent catalogue/search requests took 0.480 / 0.320 / 0.302 seconds. These are four point-in-time diagnostics, not a normal-load benchmark or monthly availability result.

The prepared controller retains the existing workload and thresholds for 100 then 250 VUs. Localhost fixtures checked positive execution, request draining, cache/timing summaries, missing-marker preflight rejection and a headerless simulated 503 stopping before the next stage. Fixture users/durations were deliberately reduced and are not performance evidence. Cookie values were not recorded. No public load run was started.

The latest verified CI evidence is in 04_Execution_Evidence/CI_Cache_33745b5. Previous curated report/workbook baselines remain attributed to their earlier sources pending the final packet update. Earlier failed load evidence is unchanged. BOOK-NF-002 / OBP-48 remain open until the actual targeted execution is assessed; 500 users are not included in the prepared run.
