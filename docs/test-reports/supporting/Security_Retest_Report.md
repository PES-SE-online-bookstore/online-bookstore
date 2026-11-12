# OBP-47 post-fix scoped security review — 9 November 2026

Source: afdb5b14bec00e3f36d287284bd03d3a116fe7f4. Downloaded pinned source snapshot matched 79 hosted file fingerprints. Source was inspected without importing/executing application code. Historical reports and raw findings remain unchanged.

| Check | Result |
|---|---|
| Hosted security regression | 15/15 Passed within the inspected 268-pass PostgreSQL run; main CI also succeeded on identical tree |
| Password/session/RBAC/input evidence | Existing manual samples plus mapped hosted regression retained |
| Public TLS 1.0 / 1.1 | Both rejected by peer protocol-version alert |
| Public TLS 1.2 / 1.3 | Both accepted; hostname/certificate-chain verification enabled |
| HTTP redirects | Eight sampled paths returned 301; corresponding HTTPS requests returned 200 |
| Bandit 1.9.4 | 40 files / 2603 lines; one B105 raw alert, reviewed false positive; zero scan errors; exit 1 retained |
| Dependency advisories | 14 source pins and 20 CI snapshot packages: zero known vulnerabilities; zero skipped packages |
| ZAP 2.17.0 | 62 passive rules; 16 allowlisted GETs; 23 raw alert instances: 8 Medium, 3 Low, 12 Informational; zero High |
| Missing CSP / HSTS retests | No missing-header alerts remain on eight sampled HTTPS pages |
| Application PostgreSQL TLS | Developer startup report: TLSv1.3 / TLS_AES_256_GCM_SHA384; attributed report, not independent Render log access |
| Real outbound mail | User confirms successful reset journey and correct Order #6 Confirmed/Shipped/Delivered mails at approximately five seconds each |

## Triage

Bandit B105 flags the literal https://oauth2.googleapis.com/token because its variable is named token_url. This is a public endpoint URL, not a hardcoded credential. No source change, suppression or test weakening was used; raw result remains.

The eight Medium ZAP instances are one repeated policy observation: CSP img-src allows any HTTPS host. This supports arbitrary external cover URLs, but remains a broad policy and an open hardening/risk-review item. It is not a demonstrated XSS exploit and is not automatically accepted as risk-free. Consider approved hosts or an image proxy when practical.

Three Low cookie alerts concern csrftoken, not the authenticated session cookie. Informational cache/reflection/session-detection items are retained with scoped analysis. No private-cache leak or executable XSS was demonstrated by these public passive samples. Existing isolated PostgreSQL regression exercises adversarial input/CSRF/authorization conditions; this is not a full penetration/fuzz campaign.

## Completion limits

Scoped current-build checks are executed and documented. Security acceptance remains qualified by the approved mock/tokenization exception, open image-source hardening observation, Blueprint startup-check drift and runtime transport-evidence limits. Do not claim full original-SRS tokenization or exhaustive security acceptance. No payment, review eligibility, capacity or recovery pass follows from these scans.

The scanner used a fresh local tool home, including its initialization/add-on setup; the effective 62-rule inventory is preserved in metadata. No spider, active scan, login, form submission or application data write occurred. The scanner process was shut down after the queue drained and reports were saved. No project dependency changes, Git/Jira publication or OBP-49 execution occurred.

Raw reports: bandit.json, pip-audit-source.json, pip-audit-ci-snapshot.json, zap-alerts.json, zap-passive-report.html/json, tls-version-results.json. Triage and SHA manifests are alongside this report.
