# Deployment review — 9 November 2026

Main commit **afdb5b14bec00e3f36d287284bd03d3a116fe7f4** is the merged result of PR #2. GitHub independently confirms main push run 42590177097 completed successfully, including the test/report/upload steps and Production Health Check.

The merged source tree is exactly the same Git tree as the inspected PR temporary merge (edcd676c2d68922af23bc1786f936a7be26a1322). The authoritative inspected structured result remains the PR artifact: 268 Passed, 18 Unit / 250 Integration, statement 1095/1200 (91.25%), branch 239/286 (83.57%). Main has its own uploaded artifact; its metadata was verified but its archive has not been downloaded/inspected. Do not relabel the PR artifact as the main artifact.

The developer reports Render deployment dep-dboopspsrm7s73clbv20 went live at 2026-11-09T09:06:39Z on the full main SHA. Startup output at 09:06:26Z states: TLS is active: TLSv1.3; cipher: TLS_AES_256_GCM_SHA384. Accept as attributed developer-provided application-connection evidence; no authenticated Render logs were accessed here.

Independent public GET samples at approximately 09:13:31Z confirmed health 200 with healthy/database available, login and catalogue 200, enforcing CSP (no report-only header), and HSTS max-age=3600. Catalogue contains three new cover placeholders and no actual cover img in this unfiltered sample. This confirms the new placeholder markup is served, not that a configured image fetched/displayed. No defect is inferred from blank cover URLs.

## Open deployment configuration item

Reviewed render.yaml still starts migrate followed by gunicorn without verify_postgres_tls. The developer's proposed small PR should preserve automatic verification across Blueprint syncs. This drift does not erase the current reported successful TLS handshake. Record the new final SHA if that fix deploys; refresh relevant startup/health/header evidence for it.

## Next user verification

Complete the real password-reset journey for an existing controlled QA buyer: record request/receipt times, follow the link, set a private new password, verify old-password rejection and new-password login, then verify the original link is unusable. Do not share passwords, reset tokens or full email contents. There is no need to wait thirty minutes; the clock-controlled expiry assertion already passed in hosted QA. Screenshot only on failure/ambiguity.

Then combine remaining timed order-status email, seller/cover and checkout/cancellation samples with the final deployed journey where possible. Existing manual batches remain evidence. OBP-48 still needs supported measurements/dispositions; no full uptime/capacity/recovery pass is implied. OBP-49 remains prepared/held and was not executed here.

For the final packet, preserve main's artifact qa-results-afdb5b14bec00e3f36d287284bd03d3a116fe7f4-1 from run 42590177097 if available; no additional CI rerun is requested by this review.

This review made only unauthenticated public GET observations and local evidence updates. No application data mutation, Git changes, merges, PR submissions, deployments or OBP-49 tests were performed.
