# Branch Coverage Report

Source commit: `f6d7d85eb6c93599c5e0bd05f6b6560aa1e88da3`

Tracked changes: None

Run: `20261112T072332130989Z`; started: 2026-11-12T07:23:32.130978+00:00

Environment: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43; Python 3.11.18

Settings: `config.settings`

Test process exit code: 0

Evidence applies to this source and test environment. The deployed version is unverified.

Measured scope: accounts, books, cart, orders, config. Test modules and migrations are excluded; exact configuration is stored in coverage-config.txt.

Covered: 247; total: 294; coverage: 84.01%.

No separate branch threshold is assumed.

| File | Coverage % |
|---|---:|
| accounts/__init__.py | 100.00 |
| accounts/admin.py | 100.00 |
| accounts/apps.py | 100.00 |
| accounts/forms.py | 90.00 |
| accounts/models.py | 100.00 |
| accounts/urls.py | 100.00 |
| accounts/views.py | 100.00 |
| accounts/management/__init__.py | 100.00 |
| accounts/management/commands/__init__.py | 100.00 |
| accounts/management/commands/verify_postgres_tls.py | 83.33 |
| books/__init__.py | 100.00 |
| books/admin.py | 100.00 |
| books/apps.py | 100.00 |
| books/catalogue_cache.py | 100.00 |
| books/forms.py | 78.57 |
| books/models.py | 100.00 |
| books/signals.py | 100.00 |
| books/urls.py | 100.00 |
| books/views.py | 85.11 |
| cart/__init__.py | 100.00 |
| cart/admin.py | 100.00 |
| cart/apps.py | 100.00 |
| cart/forms.py | 70.00 |
| cart/models.py | 100.00 |
| cart/urls.py | 100.00 |
| cart/views.py | 80.43 |
| config/__init__.py | 100.00 |
| config/asgi.py | 100.00 |
| config/email_backends.py | 83.33 |
| config/health.py | 100.00 |
| config/settings.py | 50.00 |
| config/urls.py | 100.00 |
| config/wsgi.py | 100.00 |
| orders/__init__.py | 100.00 |
| orders/admin.py | 100.00 |
| orders/apps.py | 100.00 |
| orders/email_notifications.py | 66.67 |
| orders/models.py | 100.00 |
| orders/services.py | 83.33 |
| orders/signals.py | 83.33 |
| orders/urls.py | 100.00 |
| orders/views.py | 100.00 |

Source: ../coverage.xml. Missing lines/branches: ../coverage.txt and ../html/index.html.
