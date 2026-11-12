# Final test summary

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

Final CI: 294 Passed,18 Unit/276 Integration; duration 66.125s. Statements 91.85%, branches 84.01%, defined core 92.68%. Case register: 373 records,368 Passed,2 Failed,3 Not run;31 requirement mappings.

| Finding/limit | Final disposition |
|---|---|
| 250-user browsing response time | Failed; p90 3.807/3.792 s exceeded 3 s; original evidence retained |
| Admin order-edit breadcrumb links | Unresolved WCAG 1.4.1 automated finding; user chose to retain it |
| 500-user capacity | Not tested; no further execution planned |
| Monthly 99.5% availability | Not tested; no full-month history |
| Backup/recovery | Fresh scoped checks Passed, schedule improved; historical >24h gap/full production RPO/RTO remain unverified |
| Accessibility limits | Manual sweeps/checks reported satisfactory; per-node ratios/role details and screen-reader speech not supplied; no full conformance claim |
| Broad HTTPS CSP image sources | Retained nonblocking security observation |
| Mock payment / review eligibility | No gateway tokenization or genuine paid-payment acceptance; paid-purchase-only review restriction not established |
| Developer implementation gaps | Seller approval/rejection notifications (D-07) and application request throttling (D-08) remain unimplemented per the developer register; decision statuses retained |
| Registration error association | Reference visible and target existence user-reported; local broken-reference result not promoted to confirmed live defect |

Historical reset expiry, assigned seller, cover rendering and real email delivery findings were fixed/retested or revised as documented. The email-login assertion was revised to username/session behavior; it was not hidden as an application fix. Original failed CI/run evidence remains preserved.

Checkout performance and current-build isolated recovery Passed. The scoped accessibility assessment is complete with an unresolved breadcrumb finding and recorded evidence limits. Eight functional/security/regression work items retain their scoped completed execution; OBP-48 revised-scope execution is complete with findings and untested/unverified targets. Final QA documents are ready for user publication, not an all-requirements acceptance statement.
