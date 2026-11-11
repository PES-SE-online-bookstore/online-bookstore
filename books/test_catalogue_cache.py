"""OBP-48 catalogue query-result cache: expiry, invalidation, query separation,
session separation, CSP behaviour and diagnostics.

These are request/database integration tests. They do not measure load
capacity; that needs the hosted load stages.
"""

import re
import time
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from books.models import Book
from qa.catalog import requirement


User = get_user_model()
PASSWORD = "Cache-QA!5tR81"
CATALOGUE = reverse("books:book_catalogue")


def make_book(title, **fields):
    defaults = {
        "author": "Cache Author",
        "isbn": f"978{abs(hash(title)) % 10**10:010d}",
        "description": "Cache fixture",
        "category": "Cache Fiction",
        "price": Decimal("100.00"),
        "stock_quantity": 5,
        "is_available": True,
        "approval_status": Book.ApprovalStatus.APPROVED,
    }
    defaults.update(fields)
    return Book.objects.create(title=title, **defaults)


def titles(response):
    return [book.title for book in response.context["books"]]


@override_settings(CATALOGUE_CACHE_SECONDS=30)
class CatalogueCacheTestCase(TestCase):
    qa_level = "Integration"
    qa_requirements = ("BOOK-NF-002", "BOOK-F-005")

    def setUp(self):
        caches["catalogue"].clear()
        self.addCleanup(caches["catalogue"].clear)

    def get(self, client=None, **params):
        return (client or self.client).get(CATALOGUE, params)


class CacheExpiryTests(CatalogueCacheTestCase):
    def setUp(self):
        super().setUp()
        make_book("Expiry Alpha")

    def test_first_request_misses_and_repeat_hits(self):
        self.assertEqual(self.get()["X-Catalogue-Cache"], "MISS")
        self.assertEqual(self.get()["X-Catalogue-Cache"], "HIT")

    def test_hit_runs_no_queries_and_miss_runs_three(self):
        with self.assertNumQueries(3):
            self.get()
        with self.assertNumQueries(0):
            response = self.get()
        self.assertEqual(titles(response), ["Expiry Alpha"])

    def test_entry_is_rebuilt_after_timeout(self):
        self.get()
        # Bypass invalidation: change the row without signals.
        Book.objects.filter(title="Expiry Alpha").update(title="Expiry Changed")
        self.assertEqual(titles(self.get()), ["Expiry Alpha"])

        later = time.time() + 31
        with patch("django.core.cache.backends.locmem.time") as clock:
            clock.time.return_value = later
            response = self.get()

        self.assertEqual(response["X-Catalogue-Cache"], "MISS")
        self.assertEqual(titles(response), ["Expiry Changed"])

    def test_entry_is_still_served_just_before_timeout(self):
        self.get()
        Book.objects.filter(title="Expiry Alpha").update(title="Expiry Changed")

        sooner = time.time() + 25
        with patch("django.core.cache.backends.locmem.time") as clock:
            clock.time.return_value = sooner
            response = self.get()

        self.assertEqual(response["X-Catalogue-Cache"], "HIT")

    @override_settings(CATALOGUE_CACHE_SECONDS=0)
    def test_zero_seconds_disables_the_cache(self):
        for _ in range(2):
            with self.assertNumQueries(3):
                response = self.get()
            self.assertEqual(response["X-Catalogue-Cache"], "BYPASS")
        # Only the invalidation version token may exist; no catalogue data.
        data_keys = [
            key for key in caches["catalogue"]._cache
            if not key.endswith("catalogue:version")
        ]
        self.assertEqual(data_keys, [])


class CacheInvalidationTests(CatalogueCacheTestCase):
    def setUp(self):
        super().setUp()
        self.book = make_book("Invalidation Alpha")
        self.get()  # populate

    def assert_fresh(self, expected_titles):
        response = self.get()
        self.assertEqual(response["X-Catalogue-Cache"], "MISS")
        self.assertEqual(titles(response), expected_titles)

    def test_new_approved_book_appears_immediately(self):
        make_book("Invalidation Beta")
        self.assert_fresh(["Invalidation Alpha", "Invalidation Beta"])

    def test_edited_title_and_price_appear_immediately(self):
        self.book.title = "Invalidation Renamed"
        self.book.price = Decimal("55.00")
        self.book.save()
        response = self.get()
        self.assertEqual(titles(response), ["Invalidation Renamed"])
        self.assertContains(response, "INR 55.00")

    def test_approving_a_pending_book_publishes_it(self):
        pending = make_book(
            "Invalidation Pending",
            approval_status=Book.ApprovalStatus.PENDING,
        )
        self.assertEqual(titles(self.get()), ["Invalidation Alpha"])
        pending.approval_status = Book.ApprovalStatus.APPROVED
        pending.save()
        self.assert_fresh(["Invalidation Alpha", "Invalidation Pending"])

    @requirement("BOOK-NF-002", "BOOK-F-016")
    def test_rejecting_a_book_removes_it_and_its_category(self):
        self.book.approval_status = Book.ApprovalStatus.REJECTED
        self.book.save()
        response = self.get()
        self.assertEqual(titles(response), [])
        self.assertEqual(list(response.context["categories"]), [])

    def test_deleting_a_book_removes_it(self):
        self.book.delete()
        self.assert_fresh([])

    @requirement("BOOK-NF-002", "BOOK-F-017")
    def test_admin_bulk_deactivate_invalidates_despite_bypassing_save(self):
        admin = User.objects.create_superuser("cache_admin", password=PASSWORD)
        self.client.force_login(admin)
        response = self.client.post(
            reverse("admin:books_book_changelist"),
            {"action": "deactivate_listings", "_selected_action": [self.book.pk]},
        )
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        self.assert_fresh([])

    def test_category_list_follows_new_category(self):
        make_book("Invalidation Gamma", category="Cache History")
        response = self.get()
        self.assertEqual(
            list(response.context["categories"]),
            ["Cache Fiction", "Cache History"],
        )


class CacheQuerySeparationTests(CatalogueCacheTestCase):
    qa_requirements = ("BOOK-NF-002", "BOOK-F-005", "BOOK-F-006")

    def setUp(self):
        super().setUp()
        make_book("Separation Python Guide", category="Programming", price="300")
        make_book("Separation Poetry Book", category="Poetry", price="50")
        for n in range(13):
            make_book(f"Separation Filler {n:02}", category="Filler", price="10")

    def test_different_searches_get_different_results(self):
        self.assertEqual(titles(self.get(q="Python")), ["Separation Python Guide"])
        self.assertEqual(titles(self.get(q="Poetry")), ["Separation Poetry Book"])
        cached = self.get(q="Python")
        self.assertEqual(cached["X-Catalogue-Cache"], "HIT")
        self.assertEqual(titles(cached), ["Separation Python Guide"])

    def test_categories_do_not_share_entries(self):
        self.assertEqual(
            titles(self.get(category="Programming")),
            ["Separation Python Guide"],
        )
        response = self.get(category="Poetry")
        self.assertEqual(response["X-Catalogue-Cache"], "MISS")
        self.assertEqual(titles(response), ["Separation Poetry Book"])

    def test_price_ranges_do_not_share_entries(self):
        self.assertEqual(
            titles(self.get(min_price="200")),
            ["Separation Python Guide"],
        )
        self.assertEqual(
            titles(self.get(max_price="60", category="Poetry")),
            ["Separation Poetry Book"],
        )

    def test_pages_do_not_share_entries(self):
        first = titles(self.get())
        second = titles(self.get(page=2))
        self.assertEqual(len(first), 12)
        self.assertEqual(len(second), 3)
        self.assertFalse(set(first) & set(second))
        self.assertEqual(titles(self.get(page=2)), second)

    def test_invalid_and_out_of_range_pages_resolve_like_before(self):
        first = titles(self.get())
        self.assertEqual(titles(self.get(page="not-a-page")), first)
        response = self.get(page=999)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(response.context["paginator"].count, 15)

    def test_search_box_echoes_this_request_not_a_cached_one(self):
        self.get(q="Python")
        response = self.get(q="  Python  ")
        self.assertEqual(response["X-Catalogue-Cache"], "HIT")
        self.assertEqual(response.context["query"], "Python")
        self.assertContains(response, 'value="Python"')


class CacheSessionSeparationTests(CatalogueCacheTestCase):
    qa_requirements = ("BOOK-NF-002", "BOOK-SR-004")

    def setUp(self):
        super().setUp()
        make_book("Session Shared Book")
        self.buyer = User.objects.create_user("cache_buyer_qa", password=PASSWORD)
        Profile.objects.create(user=self.buyer, role=Profile.Role.BUYER)
        self.seller = User.objects.create_user("cache_seller_qa", password=PASSWORD)
        Profile.objects.create(user=self.seller, role=Profile.Role.SELLER)

    def test_anonymous_hit_after_logged_in_miss_shows_no_user(self):
        self.client.force_login(self.buyer)
        self.assertContains(self.get(), "cache_buyer_qa")
        self.client.logout()

        anonymous = self.get()
        self.assertEqual(anonymous["X-Catalogue-Cache"], "HIT")
        self.assertNotContains(anonymous, "cache_buyer_qa")
        self.assertContains(anonymous, "Log In")

    def test_each_user_sees_own_navigation_on_shared_entry(self):
        self.client.force_login(self.seller)
        self.assertContains(self.get(), "cache_seller_qa")

        self.client.force_login(self.buyer)
        response = self.get()
        self.assertEqual(response["X-Catalogue-Cache"], "HIT")
        self.assertContains(response, "cache_buyer_qa")
        self.assertNotContains(response, "cache_seller_qa")

    def test_cache_stores_no_user_or_session_data(self):
        self.client.force_login(self.buyer)
        self.get()
        session_key = self.client.session.session_key

        stored = b"".join(caches["catalogue"]._cache.values())
        self.assertNotIn(b"cache_buyer_qa", stored)
        self.assertNotIn(session_key.encode(), stored)
        self.assertTrue(
            all(key.startswith(":1:catalogue:") for key in caches["catalogue"]._cache)
        )

    def test_anonymous_hit_does_not_create_a_session(self):
        self.get()
        response = self.get()
        self.assertEqual(response["X-Catalogue-Cache"], "HIT")
        self.assertNotIn("sessionid", response.cookies)


class CacheCspTests(CatalogueCacheTestCase):
    qa_requirements = ("BOOK-NF-002", "BOOK-SR-005")

    @staticmethod
    def csp_header(response):
        return response.get("Content-Security-Policy") or response.get(
            "Content-Security-Policy-Report-Only"
        )

    def setUp(self):
        super().setUp()
        make_book("CSP Book")

    def test_each_cached_response_has_its_own_matching_nonce(self):
        nonces = []
        for _ in range(3):
            response = self.get()
            header = self.csp_header(response)
            self.assertIsNotNone(header)
            header_nonce = re.search(r"'nonce-([^']+)'", header).group(1)
            body_nonces = set(re.findall(r'nonce="([^"]+)"', response.content.decode()))
            self.assertEqual(body_nonces, {header_nonce})
            nonces.append(header_nonce)

        self.assertEqual(response["X-Catalogue-Cache"], "HIT")
        self.assertEqual(len(set(nonces)), 3)

    def test_response_is_not_marked_publicly_cacheable(self):
        self.get()
        response = self.get()
        self.assertNotIn("public", response.get("Cache-Control", ""))


class CatalogueDiagnosticsTests(CatalogueCacheTestCase):
    qa_requirements = ("BOOK-NF-002",)

    def setUp(self):
        super().setUp()
        make_book("Diagnostics Book")

    def test_server_timing_header_reports_durations(self):
        response = self.get()
        self.assertRegex(
            response["Server-Timing"],
            r"^data;dur=\d+\.\d, app;dur=\d+\.\d$",
        )

    def test_log_line_records_cache_status_and_queries_without_search_text(self):
        with self.assertLogs("books.catalogue", level="INFO") as logs:
            self.get(q="Diagnostics")
            self.get(q="Diagnostics")

        self.assertIn("cache=MISS queries=3", logs.output[0])
        self.assertIn("cache=HIT queries=0", logs.output[1])
        self.assertIn("search=yes", logs.output[1])
        self.assertNotIn("Diagnostics", "\n".join(logs.output))
