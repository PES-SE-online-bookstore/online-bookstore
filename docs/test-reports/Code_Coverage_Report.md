# Code Coverage Report

Source commit: `f6d7d85eb6c93599c5e0bd05f6b6560aa1e88da3`

Tracked changes: None

Run: `20261112T072332130989Z`; started: 2026-11-12T07:23:32.130978+00:00

Environment: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43; Python 3.11.18

Settings: `config.settings`

Test process exit code: 0

Evidence applies to this source and test environment. The deployed version is unverified.

Measured scope: accounts, books, cart, orders, config. Test modules and migrations are excluded; exact configuration is stored in coverage-config.txt.

Covered: 1183; total: 1288; coverage: 91.85%.

The SRS targets 70% of core business logic. This package-wide measurement requires an agreed core-logic scope before acceptance is claimed.

| File | Coverage % |
|---|---:|
| accounts/__init__.py | 100.00 |
| accounts/admin.py | 100.00 |
| accounts/apps.py | 100.00 |
| accounts/forms.py | 97.50 |
| accounts/models.py | 89.47 |
| accounts/urls.py | 100.00 |
| accounts/views.py | 100.00 |
| accounts/management/__init__.py | 100.00 |
| accounts/management/commands/__init__.py | 100.00 |
| accounts/management/commands/verify_postgres_tls.py | 93.75 |
| books/__init__.py | 100.00 |
| books/admin.py | 100.00 |
| books/apps.py | 100.00 |
| books/catalogue_cache.py | 100.00 |
| books/forms.py | 93.33 |
| books/models.py | 95.45 |
| books/signals.py | 100.00 |
| books/urls.py | 100.00 |
| books/views.py | 88.35 |
| cart/__init__.py | 100.00 |
| cart/admin.py | 100.00 |
| cart/apps.py | 100.00 |
| cart/forms.py | 90.62 |
| cart/models.py | 93.33 |
| cart/urls.py | 100.00 |
| cart/views.py | 88.00 |
| config/__init__.py | 100.00 |
| config/asgi.py | 0.00 |
| config/email_backends.py | 94.44 |
| config/health.py | 100.00 |
| config/settings.py | 78.69 |
| config/urls.py | 100.00 |
| config/wsgi.py | 0.00 |
| orders/__init__.py | 100.00 |
| orders/admin.py | 100.00 |
| orders/apps.py | 100.00 |
| orders/email_notifications.py | 88.00 |
| orders/models.py | 95.00 |
| orders/services.py | 93.62 |
| orders/signals.py | 88.37 |
| orders/urls.py | 100.00 |
| orders/views.py | 97.59 |

Source: ../coverage.xml. Missing lines/branches: ../coverage.txt and ../html/index.html.
