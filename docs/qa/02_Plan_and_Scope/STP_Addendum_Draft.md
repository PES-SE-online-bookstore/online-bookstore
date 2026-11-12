# System Test Plan closeout addendum

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

The project uses hybrid testing: automated Unit/Integration/regression and suitable tooling, plus targeted manual deployed journeys, real-inbox checks and accessibility samples. Automated cases are not relabelled manual. The course wording asks for manual execution; this packet describes the user's selected hybrid implementation explicitly. The 20 functional requirements each have at least eight mapped case entries, including Unit/Integration/System evidence; numeric mapping counts do not prove independent condition coverage.

Username/password with Django sessions is the revised login scope. Email remains the reset identifier. Mock payments remain in-process Pending initiation; gateway/tokenization are unimplemented. No full proposed REST/JWT/shipping interface is claimed. Original course/SRS/SAD/STP references remain in the full local reference collection.

The user ended capacity testing after existing 250-user runs and excluded month-long availability measurement. Preserve `500 users: Not tested`, `monthly availability: Not tested`, the actual failed 250-user timing and the unresolved admin breadcrumb finding. Full production RPO/RTO and untested accessibility criteria retain their limits. The twice-daily backup schedule adds headroom but does not rewrite historical failures.

CI, checkout, accessibility, capacity and recovery have different source SHAs. Historical browser reports are not silently retagged to the final build. Private credentials, cookies, reset links and database dumps are excluded from the publication packet.

## Exit assessment

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

Execution followed the revised scope. The original all-target acceptance criteria are not all met. There is no further unchanged live load/accessibility run planned; unresolved findings and unverified production criteria are reported. Final automated regression is294Passed on92247d3. Original STP/SRS/SAD documents remain intact.
