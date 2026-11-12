# Manual accessibility batch 1 — recorded results

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The user reported all eight pages Passed keyboard/focus, 200% zoom and 400% reflow, with no issues: **24 reported passes**. These are manual reports, not a new execution by the assistant. The exact browser version, execution timestamp and deployed SHA were not supplied and remain unrecorded.

| Role | Page | Keyboard/focus | 200% zoom | 400% reflow |
|---|---|---|---|---|
| buyer | `/cart/` | Passed | Passed | Passed |
| buyer | `/cart/checkout/` | Passed | Passed | Passed |
| buyer | `/orders/9/` | Passed | Passed | Passed |
| seller | `/books/seller/listings/` | Passed | Passed | Passed |
| seller | `/books/seller/create/` | Passed | Passed | Passed |
| admin | `/admin/` | Passed | Passed | Passed |
| admin | `/admin/books/book/` | Passed | Passed | Passed |
| admin | `/admin/orders/order/9/change/` | Passed | Passed | Passed |

The user explicitly chose to leave the automated admin breadcrumb finding **unresolved**. The earlier Failed finding remains; these keyboard/zoom passes do not clear it. No fix or unchanged-build rerun is requested.

The 13 incomplete axe rule occurrences (ten contrast, three table-header) and remaining applicable manual checks still need disposition. Full accessibility conformance is not established. OBP-48 remains In Progress while remaining scoped work continues. The aggregate workbook/report/publication refresh is pending.
