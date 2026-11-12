# Requirements traceability

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

All 31 requirements retain architecture/design/code references. Counts are mappings, not independent requirement passes.

| Requirement | Description | Mapped cases | Disposition |
|---|---|---|---|
| BOOK-F-001 | Registration | 26 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-002 | Username/session authentication | 22 | Verified under documented username/session revision R-001 |
| BOOK-F-003 | Account lockout | 11 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-004 | Password reset | 12 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-005 | Catalogue display | 29 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-006 | Search/filter | 32 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-007 | Book details | 12 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-008 | Cart operations | 18 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-009 | Checkout details | 16 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-010 | Payment/order creation | 12 | Approved mock scope R-002; original gateway payment/confirmation not verified |
| BOOK-F-011 | Order history | 11 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-012 | Order tracking | 12 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-013 | Cancellation/return | 27 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-014 | Seller create | 11 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-015 | Seller edit/delete | 19 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-016 | Admin approval/rejection | 22 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-017 | Inventory/account administration | 17 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-018 | Reviews | 21 | Review workflow tested; successful-paid-purchase-only eligibility not established |
| BOOK-F-019 | Wishlist | 10 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-F-020 | Status notifications | 15 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-NF-001 | Normal-load performance | 3 | Passed declared normal-load samples: historical catalogue/search p90 0.136/0.142 s; checkout run 43180348416 p90 0.1911 s, 20/20 correct during 10 browsing VUs. Distinct builds/boundaries retained. |
| BOOK-NF-002 | 500-active-user capacity | 28 | 250-user timing Failed; 100-user sample Passed; 500 users Not tested per revised execution scope. Original 500 target not demonstrated. |
| BOOK-NF-003 | Monthly availability | 4 | Monthly availability Not tested per user scope decision; no 99.5% full-month claim. |
| BOOK-NF-004 | Responsive/accessibility | 6 | Executed sampled audit with unresolved admin breadcrumb finding. Manual keyboard/zoom/form/contrast/table follow-up recorded; full conformance and screen-reader speech not established. |
| BOOK-NF-005 | Core automated coverage | 0 | Final CI 43241415099: overall statements 1183/1288=91.85%; branches 247/294=84.01%; defined 20-file core 1013/1093=92.68%, exceeds original 70% target. |
| BOOK-NF-006 | Backup/RPO/RTO | 4 | Twice-daily cron published. Fresh backup/temp restore43243243463 Passed; isolated recovery43243646709 exact 22 tables/258 rows,usable2.675s. Historical>24h gap and full production RPO/RTO remain unverified. |
| BOOK-SR-001 | Transport TLS | 8 | Scoped TLS evidence; developer DB report and runtime mail-transport limits retained |
| BOOK-SR-002 | Password protection | 4 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-SR-003 | Payment data/tokenization | 1 | Approved mock/tokenization exception; original tokenization unimplemented |
| BOOK-SR-004 | Server authorization | 62 | Verified by sampled/automated evidence within implemented scope; historical build limits retained |
| BOOK-SR-005 | Injection/XSS protection | 28 | Scoped adversarial/regression/scan evidence; image-source hardening observation open |
