# Scoped recovery rehearsal — Passed

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Run 42953060880; application source `afdb5b14bec00e3f36d287284bd03d3a116fe7f4`. Preserved artifact SHA256 `992ce42a4bd01fa0170691e835bcb66f7804c04280e39420786282da16d880d8`.

- pg_dump and pg_restore PostgreSQL 18.6 exited 0.
- All 22 tables and 182 rows exactly matched the exported source snapshot, including existing orders/payments.
- Static asset build and restored HTTP health passed.
- All seven HTTP checks passed: login form/login, catalogue, add-to-cart, checkout form/mock checkout and order detail. The script also checked the new order amount/quantity and Pending mock payment.
- Restore start to usable buyer flow: **2.371 seconds**. Script total: **11.841 seconds**. These are not whole GitHub-job or production outage timings.
- Source snapshot: 11 November 2026 03:29:46 UTC (08:59:46 IST). No raw database dump was supplied to QA.

Synthetic Order #8 and its fixture account/book exist only in the disposable restored database. No new order was created on the live bookstore by this rehearsal. No real payment or external email delivery is claimed.

**OBP48-OPS-010 is Passed within this isolated scope. BOOK-NF-006 remains partial:** historical successful backup snapshot intervals/RPO <=24h remain unverified; the measured recovery boundary excludes runner provisioning and production Render redeployment. OBP-48 remains In Progress. Failed earlier artifacts remain preserved.
