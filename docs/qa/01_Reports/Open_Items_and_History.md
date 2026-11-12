# Open findings and historical outcomes

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

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
| Registration error association | Reference visible and target existence user-reported; local broken-reference result not promoted to confirmed live defect |

Historical reset expiry, assigned seller, cover rendering and real email delivery findings were fixed/retested or revised as documented. The email-login assertion was revised to username/session behavior; it was not hidden as an application fix. Original failed CI/run evidence remains preserved.

## Developer-documented implementation gaps

The reconciled deviation register retains two additional acceptance limits reported by the developer: seller approval/rejection notifications are unimplemented (D-07), and application-level login/checkout throttling is unimplemented (D-08). Approval/visibility tests and account lockout do not establish those separate criteria. These are documented implementation gaps, not new deployed findings independently executed by this documentation update. Outstanding decision statuses are retained.
