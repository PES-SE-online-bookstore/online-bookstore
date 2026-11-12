# Non-functional evidence and limits

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

| Requirement | Final disposition |
|---|---|
| BOOK-NF-001 | Passed declared normal-load samples: historical catalogue/search p90 0.136/0.142 s; checkout run 43180348416 p90 0.1911 s, 20/20 correct during 10 browsing VUs. Distinct builds/boundaries retained. |
| BOOK-NF-002 | 250-user timing Failed; 100-user sample Passed; 500 users Not tested per revised execution scope. Original 500 target not demonstrated. |
| BOOK-NF-003 | Monthly availability Not tested per user scope decision; no 99.5% full-month claim. |
| BOOK-NF-004 | Executed sampled audit with unresolved admin breadcrumb finding. Manual keyboard/zoom/form/contrast/table follow-up recorded; full conformance and screen-reader speech not established. |
| BOOK-NF-005 | Final CI 43241415099: overall statements 1183/1288=91.85%; branches 247/294=84.01%; defined 20-file core 1013/1093=92.68%, exceeds original 70% target. |
| BOOK-NF-006 | Twice-daily cron published. Fresh backup/temp restore43243243463 Passed; isolated recovery43243646709 exact 22 tables/258 rows,usable2.675s. Historical>24h gap and full production RPO/RTO remain unverified. |
