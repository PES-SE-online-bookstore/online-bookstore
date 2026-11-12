# OBP-48 authenticated accessibility preparation

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Status: Locally validated against actual Django pages with isolated synthetic SQLite data. All 34 page/viewport samples completed, no additional orders were created and the cart was preserved. The local sample found four rule occurrences across two admin issue types and 13 incomplete rule occurrences needing review. These findings are retained; they are not yet verified on Render. Deployed scan: Not run.

The sequential scan covers 17 sampled pages at desktop 1366x768 and mobile 390x844 (34 page/viewport samples):

- Public: login, registration, reset-request form, catalogue and the named QA book detail.
- Buyer: cart, nonempty mock checkout form, order history, an existing owned order and wishlist.
- Seller: listings, create-listing form and the first owned listing's edit form.
- Admin: index, books list, orders list and the existing order's change form. No save or action button is submitted.

Only login POSTs are allowed, once per role. The harness does not submit registration/reset/reviews/order/payment/admin save forms, create orders, update carts or delete data. It does not click arbitrary links. Login sessions and database-backed session/login bookkeeping are expected authentication side effects. No persisted browser storage, raw HTML, screenshots or credentials are uploaded. Axe findings retain rule metadata and redacted CSS selectors plus selector hashes; HTML/failure summaries are omitted because pages can contain personal data.

## Private credentials

Reuse existing repository Actions secrets `QA_PERF_USERNAME` and `QA_PERF_PASSWORD` for the buyer. Add these four secrets privately in GitHub Settings → Secrets and variables → Actions:

| Name | Value |
|---|---|
| QA_A11Y_SELLER_USERNAME | Existing QA seller username |
| QA_A11Y_SELLER_PASSWORD | Its password |
| QA_A11Y_ADMIN_USERNAME | Administrator username able to view books and orders |
| QA_A11Y_ADMIN_PASSWORD | Its password |

Do not send passwords to chat or store them in source/workflow inputs. The seller must have at least one owned listing; use the existing QA seller with its prior test listing. The buyer must retain the one-item cart and existing Order #9 from the checkout run. If fixtures differ, use the actual QA title and an order belonging to that buyer. No new checkout is needed.

Absent role secrets, missing fixtures, login failures, unexpected redirects or scan errors are recorded as incomplete coverage. Missing role credentials are never interpreted as Passed. No failed-login retry loop is used.

## Publication and run

The agent does not stage, commit, push or dispatch the workflow. Publish these four QA files through a separate branch/PR:

```text
.github/workflows/qa-accessibility.yml
qa/nfr/accessibility_scan.cjs
qa/nfr/check_accessibility_guards.cjs
qa/nfr/ACCESSIBILITY.md
```

After merge and successful CI, confirm the actual live Render SHA. Run `QA Authenticated Accessibility` once on main, with that full SHA, `QA Python Advanced`, and buyer order ID `9` (or the actual owned QA order if it differs). This is a low-rate sequential scan, not another capacity test. It shares the public-load concurrency group to avoid overlapping the other QA workflows.

Download `qa-accessibility-summary-<run>-<attempt>.zip`, including failed/incomplete results, and supply it with the workflow URL. A failed job can mean real accessibility violations or incomplete coverage: inspect the artifact before changing code or rerunning.

## Interpretation and next manual checks

The tool pins Playwright 1.62.1, @axe-core/playwright 4.11.3 and axe-core 4.11.4. It checks tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`. It records violations, incomplete checks, passed/inapplicable rule counts and a horizontal-overflow sample. It does not bypass CSP. Third-party assets are blocked; this limitation must remain in the report.

Zero detected violations means only that these automated tagged checks found none in the sampled states. It does not prove full WCAG 2.1 AA conformance. Native/server validation-error states, keyboard/focus behavior, true browser zoom, meaningful alternatives/instructions and remaining applicable assistive-technology criteria require manual review. Review `incomplete` rule occurrences explicitly instead of counting them as passed. A wide admin data table needs manual interpretation; horizontal overflow alone is an observation, not automatically a WCAG failure.

After reviewing the artifact, complete one consolidated applicability/manual checklist against these actual states and any justified additional error states. Preserve original historical accessibility samples and their build attribution.

References: https://playwright.dev/docs/accessibility-testing and https://github.com/dequelabs/axe-core-npm/tree/develop/packages/playwright.
