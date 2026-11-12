# Load-testing disposition after cache retest

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Latest targeted cache retest 43035954975: 100-user browsing Passed for 120 seconds (catalogue/search p90 0.332s/0.321s). At 250 users, sustained p90 3.807s/3.792s exceeded the unchanged three-second gate and stopped the planned 120-second hold after about 30 seconds. All 9,385 started requests completed with HTTP 200; no recorded request failures or unmatched requests. Steady cache HIT share was about 99.8% per endpoint in both stages. The cache was active, but the tested deployment still missed the 250-user latency gate. 500 users were not run. See supporting/Hosted_Load_43035954975_Review.json.

The agreed single cache optimisation/retest cycle is complete with a failed 250-user timing outcome. No further unchanged public load run or tuning is proposed. Preserve [the analysis](Runs/LOAD-GHA-43035954975-1/Review.html) and [finding draft](Runs/LOAD-GHA-43035954975-1/Finding_Draft.html), then continue remaining OBP-48 evidence/dispositions and report finalization. No new code publication is required for this analysis.
