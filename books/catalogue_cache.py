"""Short-lived caching of public catalogue *query results* (BOOK-NF-002 / OBP-48).

Only database results are cached: the matching-book count, the 12 books on
one page and the category list. Rendered HTML is never cached, so every
response still gets its own CSP nonce, CSRF token, session handling and
per-user navigation. Cache keys contain only normalised catalogue filters and
a version token; they never include a user, session or cookie.

Invalidation: saving or deleting a Book (and the admin bulk-deactivate action)
replaces the version token, which orphans every catalogue entry at once. Any
change that bypasses those paths is bounded by CATALOGUE_CACHE_SECONDS.

The cache is in-process (LocMemCache). With several gunicorn workers each one
keeps its own copy; invalidation then reaches only the worker that made the
change and the others rely on expiry.
"""

import hashlib
import json
import uuid

from django.conf import settings
from django.core.cache import caches

CACHE_ALIAS = "catalogue"
VERSION_KEY = "catalogue:version"
PAGE_SIZE = 12


def cache_seconds():
    return max(int(getattr(settings, "CATALOGUE_CACHE_SECONDS", 0)), 0)


def is_enabled():
    return cache_seconds() > 0


def _cache():
    return caches[CACHE_ALIAS]


def current_version():
    # A missing (expired or culled) version simply starts a new generation,
    # which can only invalidate entries, never resurrect stale ones.
    return _cache().get_or_set(VERSION_KEY, uuid.uuid4().hex, timeout=None)


def invalidate():
    """Orphan every cached catalogue entry."""
    _cache().set(VERSION_KEY, uuid.uuid4().hex, timeout=None)


def make_key(kind, **parts):
    payload = json.dumps(
        {"version": current_version(), "kind": kind, **parts},
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"catalogue:{kind}:{digest}"


def fetch(key):
    return _cache().get(key)


def store(key, value):
    _cache().set(key, value, timeout=cache_seconds())
