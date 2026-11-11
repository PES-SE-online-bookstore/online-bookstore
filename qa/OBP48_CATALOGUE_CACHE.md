# OBP-48 catalogue cache and diagnostics (developer response)

Finding: six HTTP 503s during the 250-user browsing stage, GitHub Actions run
42969189618, deployed SHA 5752e3e02e2507be060d480c411c14f4dd70e5a9. The finding,
its thresholds and the failed result are unchanged by this work.

## Measured diagnosis (Render API, read-only, 11 Nov 2026)

| Evidence (06:09-06:13 UTC) | Observation |
|---|---|
| Service | free plan, Oregon, 1 instance; start command runs gunicorn with defaults (1 sync worker) |
| Deploys / restarts | none in the window (last deploy ended 05:45:12) |
| CPU (60 s samples) | 0.13-0.15 CPU from 06:07 to 06:11, falling to ~0 after the test |
| Memory | flat at ~98 MB (no growth, no OOM) |
| Application access log 06:10:20-06:11:20 | 1,149 lines, **all HTTP 200**; throughput flat at ~20-31 req/s from 06:10:27 |
| The six 503s (06:11:01.998-06:11:02.133) | **absent from the application log**; gunicorn served 27-30 req/s in those seconds |

Interpretation: the single worker was CPU-bound at ~27 req/s, below the offered
load at 250 users, so requests queued in front of the app (consistent with the
~8 s p90). The 503s were produced in front of gunicorn by Render's routing layer
and never reached the application. Why the platform rejected exactly those six
requests (queue, connection or time limit) is **not** visible in the available
data and is not claimed.

## Change (one limited caching change, worker configuration unchanged)

- Caches catalogue **database results only**: matching count, the 12 books on
  the page, and the category list. Rendered HTML is never cached, so each
  response keeps its own CSP nonce, CSRF/session handling and navigation.
- Key: SHA-256 of a version token plus validated `q` (whitespace-normalised),
  `category`, `min_price`, `max_price` and the resolved page number. No user,
  session or cookie data.
- Invalidation: Book save/delete signals and the admin bulk-deactivate action
  replace the version token. Anything else is bounded by the timeout.
- A full cache hit makes 0 database queries; a miss makes the same 3 as before.

| Setting | Production value |
|---|---|
| Backend | `django.core.cache.backends.locmem.LocMemCache`, alias `catalogue`, `MAX_ENTRIES` 500 |
| `CATALOGUE_CACHE_SECONDS` | 30 (env var; `0` disables without a code change) |
| Default when unset | 30 if `DEBUG=False`, 0 if `DEBUG=True` |
| gunicorn | unchanged: default 1 sync worker, 30 s timeout |

Known limits: data can be up to 30 s old after changes that bypass `save()`;
the cache is per process, so if workers are added later, invalidation reaches
only the worker that handled the change and others rely on expiry.

## Diagnostics added

- Response headers on `/books/`: `X-Catalogue-Cache: HIT|MISS|BYPASS` and
  `Server-Timing: data;dur=<ms>, app;dur=<ms>`. In the next load run, comparing
  client latency with `app;dur` separates time spent queueing in front of the
  app from time spent in Django.
- One log line per catalogue request (logger `books.catalogue`):
  `catalogue cache=HIT queries=0 data_ms=… app_ms=… search=yes|no page=N`.
  No search text, cookies, headers, user identity or bodies are logged.
- A 503 created by the platform will carry neither header; that alone
  classifies it as generated outside the application.

## Automated checks (`books/test_catalogue_cache.py`, 26 tests)

Expiry (hit/miss, 0 vs 3 queries, rebuilt after timeout, still served just
before, `0` disables), invalidation (create, edit, approve, reject, delete,
admin bulk deactivate, category list), query separation (search, category,
price, page, invalid/out-of-range pages, echoed search text), session
separation (anonymous after logged-in, per-user navigation, no user/session
data stored, no session created on a hit), CSP (fresh matching nonce on every
cached response; not publicly cacheable) and diagnostics.

## Proposed targeted verification

Rerun only the 100-user and 250-user browsing stages against the deployed
commit with the same workload, gates and thresholds. Record for each stage:
p90, error count by status, the share of `X-Catalogue-Cache: HIT`, and
`Server-Timing app;dur` vs client latency. For any 503, record status, the
presence/absence of the two diagnostic headers and sanitized platform headers
(e.g. `rndr-id`, `server`) only. If 250 users still fail, the result supports
a capacity limit of this instance rather than further application tuning; a
worker change should be a separate, later experiment.
