# Code Coverage Report

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Final automated source: `92247d31739eed30e0d769865869869b384a2ba6`. [CI run](https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43241415099). Historical manual and deployed checks retain the distinct builds/dates shown in their evidence.

Status: **QA execution completed for the revised scope, with findings and untested/unverified targets retained.**

**1183/1288 = 91.85% statement coverage.** All 294 tests Passed. XML contains 42 unique repository-relative paths; counts were independently recomputed and reconciled with the coverage summary.

BOOK-NF-005 specifies >=70% coverage of core business logic. The explicit unchanged 20-file core scope covers **1013/1093 =92.68%**, meeting that target. No uncovered file was dropped to raise coverage. Exact scope is in `supporting/Core_Coverage_Scope.json`.

| File | Covered | Total | Coverage |
|---|---|---|---|
| accounts/__init__.py | 0 | 0 | N/A |
| accounts/admin.py | 22 | 22 | 100.00% |
| accounts/apps.py | 4 | 4 | 100.00% |
| accounts/forms.py | 39 | 40 | 97.50% |
| accounts/models.py | 17 | 19 | 89.47% |
| accounts/urls.py | 4 | 4 | 100.00% |
| accounts/views.py | 54 | 54 | 100.00% |
| accounts/management/__init__.py | 0 | 0 | N/A |
| accounts/management/commands/__init__.py | 0 | 0 | N/A |
| accounts/management/commands/verify_postgres_tls.py | 15 | 16 | 93.75% |
| books/__init__.py | 0 | 0 | N/A |
| books/admin.py | 43 | 43 | 100.00% |
| books/apps.py | 6 | 6 | 100.00% |
| books/catalogue_cache.py | 26 | 26 | 100.00% |
| books/forms.py | 42 | 45 | 93.33% |
| books/models.py | 42 | 44 | 95.45% |
| books/signals.py | 8 | 8 | 100.00% |
| books/urls.py | 4 | 4 | 100.00% |
| books/views.py | 235 | 266 | 88.35% |
| cart/__init__.py | 0 | 0 | N/A |
| cart/admin.py | 1 | 1 | 100.00% |
| cart/apps.py | 4 | 4 | 100.00% |
| cart/forms.py | 29 | 32 | 90.62% |
| cart/models.py | 42 | 45 | 93.33% |
| cart/urls.py | 4 | 4 | 100.00% |
| cart/views.py | 132 | 150 | 88.00% |
| config/__init__.py | 0 | 0 | N/A |
| config/asgi.py | 0 | 4 | 0.00% |
| config/email_backends.py | 51 | 54 | 94.44% |
| config/health.py | 15 | 15 | 100.00% |
| config/settings.py | 48 | 61 | 78.69% |
| config/urls.py | 5 | 5 | 100.00% |
| config/wsgi.py | 0 | 4 | 0.00% |
| orders/__init__.py | 0 | 0 | N/A |
| orders/admin.py | 20 | 20 | 100.00% |
| orders/apps.py | 6 | 6 | 100.00% |
| orders/email_notifications.py | 22 | 25 | 88.00% |
| orders/models.py | 76 | 80 | 95.00% |
| orders/services.py | 44 | 47 | 93.62% |
| orders/signals.py | 38 | 43 | 88.37% |
| orders/urls.py | 4 | 4 | 100.00% |
| orders/views.py | 81 | 83 | 97.59% |

Coverage was collected with branches enabled over accounts, books, cart, orders and config. Test modules, migrations and tooling/results are excluded by the retained configuration. The combined line/branch percentage in coverage.txt is not substituted for statement-only coverage. Source hashes, commands and exit codes were inspected; overall/core metrics retain their defined denominators. Coverage is not proof of all requirements or deployed performance.
