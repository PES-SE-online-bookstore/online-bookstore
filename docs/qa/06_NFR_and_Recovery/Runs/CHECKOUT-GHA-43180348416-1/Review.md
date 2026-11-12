# OBP48-PERF-003 — completed checkout performance

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Result: **Passed for the declared normal-load mock-checkout scenario.**

Workflow: https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43180348416

Reported live and harness commit: `f6d7d85eb6c93599c5e0bd05f6b6560aa1e88da3`. Live build attribution is user-supplied; the artifact agrees.

| Check | Verified result |
|---|---|
| Mock checkouts | 20 submitted, 20 distinct completed orders, all correctness checks passed |
| Checkout p90 | 191.100 ms; target <=5,000 ms |
| Slowest checkout | 221.300 ms |
| Samples <=5 seconds | 20/20 |
| Created orders | #9–#28, Pending order/Pending Test Card payment |
| Fixture | QA Python Advanced, quantity 1, unit price and total INR 450.00 |
| Background browsing | 10 VUs held for 300.568 seconds |
| Browsing requests | 1524 started and completed; all HTTP 200; zero failures/unaccounted requests |
| Catalogue steady p90 | 87.231 ms; 887 requests |
| Search steady p90 | 88.101 ms; 559 requests |
| Browser | Chromium 151.0.7922.34 |

Independent review recomputed p90 values and counts from the checkout samples and request CSV, checked all twenty item/quantity/unit-price/total/address/buyer/order/payment assertions, verified transactions stayed within the steady interval, and checked the duplicate embedded browser record and ZIP CRC.

The full run was 08:08:12–08:13:38 UTC on 12 November 2026 (13:38:12–13:43:38 IST). The operator reports no errors; CPU/memory values, a separate restart statement and exact log-review range were not supplied. These observations are not substituted with load-generator resource readings.

Timing measures checkout POST navigation start through loadEventEnd of the correct Checkout Submitted page, including same-origin assets. Login, form preparation and later order-detail verification are outside the timed interval. Third-party assets are blocked. Correctness verification of the order detail follows every submission.

This closes OBP48-PERF-003 for one sequential mock-checkout browser alongside ten anonymous browsing VUs. BOOK-NF-001 now has checkout timing evidence alongside its historical catalogue/search samples, with distinct build attribution. It does not establish simultaneous checkout capacity, real payment processing, or every page's performance on the latest build.

**OBP-48 remains In Progress.** The earlier failed 250-user timing gate and unexecuted 500-user target remain. Accessibility, monthly availability and full production recovery findings remain separate. Do not rerun checkout or delete test orders as part of this evidence review.

The new execution result is preserved here. The case workbook, aggregate reports and selected publication packet still require a consolidated refresh; their older counts are not silently relabelled by this result.

Artifact SHA-256: `f5768da35e12252383ce552fdd4e21d1fa781bb8c1c7a99e9fecadee25cce505`.
