# Branch Coverage Report

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

**247/294 = 84.01% branch coverage.** All 294 tests Passed. XML contains 42 unique repository-relative paths; counts were independently recomputed and reconciled with the coverage summary.

No separate branch threshold is invented. Files with zero branch opportunities are N/A, not 100% acceptance. Branch coverage counts executed branch exits; it is distinct from statement coverage.

| File | Covered | Total | Coverage |
|---|---|---|---|
| accounts/__init__.py | 0 | 0 | N/A |
| accounts/admin.py | 2 | 2 | 100.00% |
| accounts/apps.py | 0 | 0 | N/A |
| accounts/forms.py | 9 | 10 | 90.00% |
| accounts/models.py | 0 | 0 | N/A |
| accounts/urls.py | 0 | 0 | N/A |
| accounts/views.py | 20 | 20 | 100.00% |
| accounts/management/__init__.py | 0 | 0 | N/A |
| accounts/management/commands/__init__.py | 0 | 0 | N/A |
| accounts/management/commands/verify_postgres_tls.py | 5 | 6 | 83.33% |
| books/__init__.py | 0 | 0 | N/A |
| books/admin.py | 8 | 8 | 100.00% |
| books/apps.py | 0 | 0 | N/A |
| books/catalogue_cache.py | 0 | 0 | N/A |
| books/forms.py | 11 | 14 | 78.57% |
| books/models.py | 0 | 0 | N/A |
| books/signals.py | 0 | 0 | N/A |
| books/urls.py | 0 | 0 | N/A |
| books/views.py | 80 | 94 | 85.11% |
| cart/__init__.py | 0 | 0 | N/A |
| cart/admin.py | 0 | 0 | N/A |
| cart/apps.py | 0 | 0 | N/A |
| cart/forms.py | 7 | 10 | 70.00% |
| cart/models.py | 0 | 0 | N/A |
| cart/urls.py | 0 | 0 | N/A |
| cart/views.py | 37 | 46 | 80.43% |
| config/__init__.py | 0 | 0 | N/A |
| config/asgi.py | 0 | 0 | N/A |
| config/email_backends.py | 10 | 12 | 83.33% |
| config/health.py | 0 | 0 | N/A |
| config/settings.py | 6 | 12 | 50.00% |
| config/urls.py | 0 | 0 | N/A |
| config/wsgi.py | 0 | 0 | N/A |
| orders/__init__.py | 0 | 0 | N/A |
| orders/admin.py | 0 | 0 | N/A |
| orders/apps.py | 0 | 0 | N/A |
| orders/email_notifications.py | 4 | 6 | 66.67% |
| orders/models.py | 0 | 0 | N/A |
| orders/services.py | 15 | 18 | 83.33% |
| orders/signals.py | 15 | 18 | 83.33% |
| orders/urls.py | 0 | 0 | N/A |
| orders/views.py | 18 | 18 | 100.00% |

Coverage was collected with branches enabled over accounts, books, cart, orders and config. Test modules, migrations and tooling/results are excluded by the retained configuration. The combined line/branch percentage in coverage.txt is not substituted for statement-only coverage. Source hashes, commands and exit codes were inspected; overall/core metrics retain their defined denominators. Coverage is not proof of all requirements or deployed performance.
