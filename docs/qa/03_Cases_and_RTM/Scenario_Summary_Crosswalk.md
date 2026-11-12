# Scenario-summary crosswalk

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The developer's32 summary scenarios link to the 373-row detailed register below. Requirement mapping is not acceptance or proof that every method tests the entire scenario. Exact full case IDs are in the adjacent JSON.

| Scenario | Requirements | Linked case entries | Result summary |
|---|---|---|---|
| TC-Auth-01 | BOOK-F-001 | 26 | Passed |
| TC-Auth-02 | BOOK-F-002 | 22 | Passed |
| TC-Auth-03 | BOOK-F-003 | 11 | Passed |
| TC-Auth-04 | BOOK-F-004 | 12 | Passed (the expiry check failed on 2026-11-03 and was fixed; see `qa/history/`) |
| TC-Cat-01 | BOOK-F-005 | 29 | Passed |
| TC-Cat-02 | BOOK-F-006 | 32 | Passed |
| TC-Cat-03 | BOOK-F-007 | 12 | Passed |
| TC-Cart-01 | BOOK-F-008 | 18 | Passed |
| TC-Cart-02 | BOOK-F-009 | 16 | Passed |
| TC-Cart-03 | BOOK-F-010 | 12 | Passed against the **mock** only; gateway acceptance not verified |
| TC-Ord-01 | BOOK-F-011 | 11 | Passed |
| TC-Ord-02 | BOOK-F-012 | 12 | Passed (manual status, no shipping API: D-06) |
| TC-Ord-03 | BOOK-F-013 | 27 | Passed |
| TC-Sell-01 | BOOK-F-014 | 11 | Passed |
| TC-Sell-02 | BOOK-F-015 | 19 | Passed |
| TC-Admin-01 | BOOK-F-016 | 22 | Approval/visibility checks Passed. Seller decision notification is unimplemented per developer D-07; full notification criterion not claimed Passed. |
| TC-Admin-02 | BOOK-F-017 | 17 | Passed |
| TC-Rev-01 | BOOK-F-018 | 21 | Passed within ordered-item/mock-payment scope. Verified-paid-purchase-only enforcement is not established. |
| TC-Rev-02 | BOOK-F-019 | 10 | Passed |
| TC-Rev-03 | BOOK-F-020 | 15 | Automated checks Passed. User reports correct real Confirmed/Shipped/Delivered messages for Order #6, each arriving in about five seconds. These are samples, not a delivery percentile. |
| TC-Perf-01 | BOOK-NF-001 | 3 | Passed those declared samples: catalogue/search p90 0.136/0.142 s; checkout 20/20 correct, p90 0.1911 s during ten browsing VUs. Build/timing boundaries retained. Separate 250-user capacity failure is not a normal-load pass. |
| TC-Perf-02 | BOOK-NF-002 | 28 | 500 users Not tested per user execution scope. Latest 250-user timing Failed at 3.807/3.792 s against 3 s; 100-user sample Passed. Earlier 503 evidence preserved separately. |
| TC-Perf-03 | BOOK-NF-002, BOOK-NF-001 | 31 | 26 cache Integration tests Passed. Correctness support does not establish concurrent-user capacity. |
| TC-Avail-01 | BOOK-NF-003 | 4 | Health integration checks Passed. Full-month 99.5% availability Not tested per user scope decision. |
| TC-UX-01 | BOOK-NF-004 | 6 | Executed sampled audit: 34/34 scans; unresolved admin breadcrumb finding; 24 manual keyboard/zoom/reflow passes plus form/contrast/table reports. Original incomplete checks/evidence limits retained; full conformance and speech not established. |
| TC-Cov-01 | BOOK-NF-005 | 0 | Defined 20-file core: 1013/1093=92.68%, exceeds 70%. Overall statements 91.85%, branches 84.01%. Scope listed in Core_Coverage_Scope.json. |
| TC-Ops-02 | BOOK-NF-006 | 4 | Fresh backup/temp restore Passed. Isolated recovery matched 22 tables/258 rows, usable 2.675 s. Twice-daily schedule published. Historical >24-hour gap and complete production RPO/RTO remain unverified. |
| TC-Sec-01 | BOOK-SR-001 | 8 | Passed live; unit tests mock the connection |
| TC-Sec-02 | BOOK-SR-002 | 4 | Passed |
| TC-Sec-03 | BOOK-SR-003 | 1 | **Not verified** |
| TC-Sec-04 | BOOK-SR-004 | 62 | Passed |
| TC-Sec-05 | BOOK-SR-005 | 28 | Mapped integration checks Passed. Scoped security/static/dependency/dynamic-scan evidence is retained in the QA packet; comprehensive penetration/fuzz coverage is not established. |
