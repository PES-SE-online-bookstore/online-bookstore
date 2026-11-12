# Testing work item status

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

| Item | Scope | Execution status | Done / qualification |
|---|---|---|---|
| OBP-41 | Authentication/account management | Scoped execution complete | Registration/login/logout/protected access, lockout/recovery, reset expiry and real reset mail. Username/session revision retained. |
| OBP-42 | Catalogue/search | Scoped execution complete | Catalogue/search/filter/pagination/detail samples; seller/cover fixes; cache integration tests and separate load evidence. |
| OBP-43 | Cart/checkout | Scoped execution complete | Cart and mock checkout functional checks; twenty completed checkouts passed normal-load timing. No real gateway payment claimed. |
| OBP-44 | Orders/tracking | Scoped execution complete | Order history/details, state tracking, cancellation and return samples; mock-order scope retained. |
| OBP-45 | Seller/admin management | Scoped execution complete | Listing/approval/admin scenarios and role restrictions; seller decision notifications remain unimplemented per D-07. |
| OBP-46 | Reviews/wishlist/notifications | Scoped execution complete | Review/wishlist samples; order-status emails received with correct details. Paid-purchase-only review enforcement not established. |
| OBP-47 | Security | Scoped execution complete with observations | Password hashing, sessions, role/protected access, TLS/CSP/HSTS and recorded scans. Broad HTTPS image-source CSP observation and D-08 request-throttling gap retained. |
| OBP-48 | Non-functional requirements | Scoped execution complete with findings/untested targets | 250-user timing Failed; breadcrumb unresolved; 500/monthly Not tested; full production RPO/RTO unverified. |
| OBP-49 | End-to-end/regression | Hybrid execution complete | Four final historical browser checkpoints plus final 294-test regression. No fresh all-feature manual run on final SHA claimed. |

These are QA evidence dispositions, not remotely changed Jira states. For OBP-48, testing was performed and findings recorded under the revised scope; do not describe all original NFRs as Passed. Documentation is prepared locally and publication remains user-controlled.
