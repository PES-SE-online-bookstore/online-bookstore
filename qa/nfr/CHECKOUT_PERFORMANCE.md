# OBP-48 — completed checkout under normal browsing load

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Status: **Prepared locally; deployed performance execution Not run.**

This is OBP48-PERF-003 preparation. It does not change the failed 250-user timing result, the unexecuted 500-user target, or monthly availability findings.

## Fixed scenario and acceptance gate

- Ten independent anonymous Locust users browse catalogue/search with 3:2 random task weighting and 1–3 second think time. Ramp is one user/second, followed by ten seconds of warmup and **300 seconds of steady load**.
- One Chromium browser logs in as a dedicated QA buyer, then submits **at most 20 mock checkouts** sequentially during steady load. Intended sample starts are 10, 22, 34, ... 238 seconds into the steady interval. Actual times are retained.
- This means ten background browsing users plus one buyer browser, not ten simultaneous checkouts. It is a declared normal-load scenario, not the 500-user capacity test.
- The timed interval is the checkout **POST navigation start to loadEventEnd of the correct Checkout Submitted page**. It includes the response and same-origin page assets. Login, form preparation, human typing and the subsequent order-detail verification are outside that interval. Third-party assets are blocked.
- Require 20 distinct completed orders, correct book/quantity/prices/total/shipping snapshot, Pending order and Pending Test Card payment, zero HTTP/correctness errors, **checkout p90 <=5,000 ms**, and a completed 300-second normal browsing stage with both endpoint p90 values <=3,000 ms and all requests accounted for.
- p90 uses nearest rank (18th of 20 sorted samples). Individual samples remain visible; a p90 pass does not mean every sample took <=5 seconds.
- There is no checkout warmup submission or automatic retry. At most two samples may exceed 5 seconds; a third exceedance makes p90 acceptance impossible and stops further submissions. HTTP/correctness failures also stop the run. In-flight work is retained and browsing requests are drained.
- The script records intended submissions before clicking and captures order IDs as soon as available. If a response fails after submission, an order may exist without a captured ID. Inspect the dedicated account before rerunning; do not assume failure means no order was created.
- No order cancellation, deletion, stock alteration, account creation, address creation, or cart alteration is performed by the harness. Mock order creation currently preserves stock and cart. Do not change the fixture during a run.

## A. Prepare the fixture once

1. Register a **new Buyer** on the bookstore. Use a unique username starting with `qa_perf_`, for example `qa_perf_20261111_01`, a strong private password, and a QA email address. Do not use an administrator/seller or a real customer's account.
2. Log in as this buyer. Add **exactly one QA book** to the cart with **quantity 1**. The title must begin with `QA`. The book must be approved, available and have stock >=1. Record its exact current title and unit price with two decimals. You may reuse an existing QA book; do not change its price merely for this test.
3. In a separate browser/private window, sign in to `/admin/`. Open **Cart → Shipping addresses → Add shipping address**. Select the new `qa_perf_...` buyer and enter exactly the following synthetic fixture. This avoids placing a setup order:

| Field | Value |
|---|---|
| User | The new dedicated QA buyer |
| Full name | QA Performance Buyer |
| Address line 1 | 1 QA Test Street |
| Address line 2 | Leave blank |
| City | Bengaluru |
| State | Karnataka |
| Postal code | 560001 |
| Country | India |
| Phone number | 0000000000 |
| Is default | Checked |

4. Save. Ensure this buyer has **exactly one saved shipping address**. Do not modify other users' addresses.
5. In the buyer's window, open `/cart/checkout/`. Verify one intended book, quantity 1, expected total, one saved synthetic address and Test Card sandbox selection. **Do not click Place Order.** A screenshot is not required for preparation.
6. Send only the buyer **username, exact book title, unit price and “fixture ready”** to the QA chat. Keep the password private.

## B. Configure limited credentials privately

In GitHub repository **Settings → Secrets and variables → Actions → New repository secret**, create:

| Secret name | Secret value |
|---|---|
| QA_PERF_USERNAME | The dedicated buyer username |
| QA_PERF_PASSWORD | That buyer's password |

These credentials are used only by the login/preflight and measurement steps. No administrator, email-provider or database credentials are needed. Do not paste the password into the chat, workflow inputs or source code.

## C. Publish only the QA harness yourself

The agent has not committed, staged or pushed anything. The existing capacity workflow is unchanged. These five files form this change:

```text
.github/workflows/qa-checkout-performance.yml
qa/nfr/controlled_load.py
qa/nfr/checkout_performance.cjs
qa/nfr/check_checkout_fixture.cjs
qa/nfr/CHECKOUT_PERFORMANCE.md
```

Review `git status --short` first. If other work appears, leave it untouched and ask for adjusted commands. Do not mix the report publication packet into this commit.

```powershell
Set-Location -LiteralPath 'C:/Users/abdullah/Documents/sem5DUMP/SE/SE Mini Project/qa-recovery-publish' -ErrorAction Stop
git status --short
git diff -- qa/nfr/controlled_load.py
git switch -c qa/checkout-performance
if ($LASTEXITCODE -ne 0) { throw 'Branch creation failed. Stop.' }
git add -- .github/workflows/qa-checkout-performance.yml qa/nfr/controlled_load.py qa/nfr/checkout_performance.cjs qa/nfr/check_checkout_fixture.cjs qa/nfr/CHECKOUT_PERFORMANCE.md
if ($LASTEXITCODE -ne 0) { throw 'Staging failed. Stop.' }
git diff --cached --stat
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'Diff check failed. Stop.' }
git commit -m "qa: prepare completed checkout normal-load measurement"
if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Stop.' }
git push -u origin qa/checkout-performance
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Stop.' }
```

Open and merge a PR from `qa/checkout-performance` into `main` using the normal repository process. The manually dispatched workflow appears after it is on the default branch. Check that CI passes. If Render deploys the merge, wait until it is live and use **that full deployed SHA** for the next step; do not keep using an older SHA merely because only QA tooling changed.

## D. Run once with monitoring

1. Keep Render Logs and Metrics open during a quiet test window. Avoid deployments, fixture changes and other load workflows until completion. This workflow shares `bookstore-public-load` concurrency with the capacity workflow, so they cannot run together through that group.
2. GitHub → **Actions → QA Completed Checkout Performance → Run workflow**. Select `main` and enter:
   - `deployed_commit`: full 40-character SHA currently live on Render.
   - `expected_book_title`: exact title from the prepared cart.
   - `expected_unit_price`: exact current unit price, e.g. `1.00`; no currency symbol.
3. Run once. The workflow first checks its safeguards against localhost, then logs in and checks the real fixture **without placing orders**. Only after that passes does it start the five-minute browsing/checkout measurement.
4. If you observe service distress, cancel the workflow. Preserve the partial evidence; cancellation/incomplete duration is not a pass. Record errors/restarts/CPU/memory observations with time range, including “none visible” if applicable.
5. Download `qa-checkout-summary-<run>-<attempt>.zip`. Send the workflow URL, ZIP path and Render observations. Do not send passwords, session cookies, database exports or raw logs containing secrets.
6. Do not automatically repeat a failed run. Review the actual failure and created-order ledger first.

## E. Review before updating results

The artifact includes `checkout-preflight/results.json`, `browser/results.json`, `summary.json`, browsing request CSV and a sanitized browser-process summary. It excludes screenshots, traces, raw HTML, cookies, passwords and address text. The synthetic fixture title and order IDs are retained for traceability.

The final decision uses both browser and controller evidence. A preflight pass, passing local fixture, or successful browser alone does **not** close the performance case if the full normal-load stage fails or is interrupted. Passing this case would close only checkout performance; OBP-48 still retains the separate capacity/availability/accessibility/recovery findings.

After review, append the new run rather than overwriting older evidence, update OBP48-PERF-003 and its requirement mapping, regenerate the four report drafts and the selected publication packet, and then continue with the next remaining OBP-48 item.
