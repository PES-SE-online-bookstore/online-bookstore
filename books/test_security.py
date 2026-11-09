"""OBP-47 focused request/security checks; no live deployment requests.

These integration tests do not establish penetration-test completeness, TLS
configuration, real payment tokenization, or production database contents.
"""

from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.html import escape

from accounts.forms import RegistrationForm
from accounts.models import Profile
from books.models import Book, WishlistItem
from qa.catalog import requirement


User = get_user_model()
PASSWORD = "Security-QA!7mW42"


class SecurityRequestIntegrationTests(TestCase):
    qa_level = "Integration"
    qa_requirements = ("BOOK-SR-005",)

    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user(username="security_buyer", password=PASSWORD)
        cls.other = User.objects.create_user(username="security_other", password=PASSWORD)
        cls.seller = User.objects.create_user(username="security_seller", password=PASSWORD)
        for user, role in ((cls.buyer, "BUYER"), (cls.other, "BUYER"), (cls.seller, "SELLER")):
            Profile.objects.create(user=user, role=role)
        cls.book = Book.objects.create(
            title="Security Fixture Book", author="QA Author", isbn="9780000003041",
            price="20.00", stock_quantity=5, is_available=True,
            approval_status=Book.ApprovalStatus.APPROVED, seller=cls.seller,
        )

    def csrf_client(self, user=None):
        client = Client(enforce_csrf_checks=True)
        if user is not None:
            client.force_login(user)
        response = client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        return client, client.cookies[settings.CSRF_COOKIE_NAME].value

    @requirement("BOOK-SR-002", "BOOK-F-001")
    def test_registered_passwords_are_verifiable_salted_hashes(self):
        stored = []
        for suffix in ("one", "two"):
            form = RegistrationForm({"username": f"security_reg_{suffix}",
                "email": f"security_{suffix}@example.com", "password": PASSWORD,
                "confirm_password": PASSWORD, "role": "BUYER"})
            self.assertTrue(form.is_valid(), form.errors)
            user = form.save()
            user.refresh_from_db()
            self.assertNotEqual(user.password, PASSWORD)
            self.assertNotIn(PASSWORD, user.password)
            self.assertIn(identify_hasher(user.password).algorithm,
                          {"pbkdf2_sha256", "argon2"})
            self.assertTrue(user.check_password(PASSWORD))
            self.assertFalse(user.check_password("Different-QA-password!"))
            stored.append(user.password)
        self.assertNotEqual(stored[0], stored[1], "Equal passwords must not produce identical stored hashes")

    @requirement("BOOK-SR-004", "BOOK-F-002")
    def test_login_rotates_pre_authentication_session(self):
        session = self.client.session
        session["qa_marker"] = "pre-authentication"
        session.save()
        previous_key = session.session_key
        response = self.client.post(reverse("login"), {"username": self.buyer.username, "password": PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session.session_key, previous_key)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.buyer.pk)
        store = import_module(settings.SESSION_ENGINE).SessionStore
        self.assertFalse(store(session_key=previous_key).exists(previous_key))

    @requirement("BOOK-SR-004", "BOOK-F-002")
    def test_logout_invalidates_copied_authenticated_cookie(self):
        self.client.force_login(self.buyer)
        previous_cookie = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        copied_client = Client()
        copied_client.cookies[settings.SESSION_COOKIE_NAME] = previous_cookie
        self.assertEqual(copied_client.get(reverse("cart:cart_detail")).status_code, 200)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        response = copied_client.get(reverse("cart:cart_detail"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("cart:cart_detail"),
                             fetch_redirect_response=False)

    def test_login_post_without_csrf_is_rejected(self):
        client, _ = self.csrf_client()
        response = client.post(reverse("login"), {"username": self.buyer.username, "password": PASSWORD})
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", client.session)

    def test_login_post_with_valid_csrf_authenticates(self):
        client, token = self.csrf_client()
        response = client.post(reverse("login"), {"username": self.buyer.username,
            "password": PASSWORD, "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(client.session["_auth_user_id"]), self.buyer.pk)

    @requirement("BOOK-SR-005", "BOOK-F-019")
    def test_wishlist_post_without_csrf_creates_nothing(self):
        client, _ = self.csrf_client(self.buyer)
        response = client.post(reverse("books:add_to_wishlist", args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(WishlistItem.objects.exists())

    @requirement("BOOK-SR-005", "BOOK-F-019")
    def test_valid_csrf_wishlist_add_is_idempotent(self):
        client, token = self.csrf_client(self.buyer)
        url = reverse("books:add_to_wishlist", args=[self.book.pk])
        for _ in range(2):
            self.assertEqual(client.post(url, {"csrfmiddlewaretoken": token}).status_code, 302)
        self.assertEqual(WishlistItem.objects.filter(buyer=self.buyer, book=self.book).count(), 1)

    @requirement("BOOK-SR-004", "BOOK-F-019")
    def test_other_buyer_cannot_view_or_remove_saved_item(self):
        item = WishlistItem.objects.create(buyer=self.buyer, book=self.book)
        client, token = self.csrf_client(self.other)
        response = client.get(reverse("books:wishlist"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.book.title)
        self.assertEqual(client.post(reverse("books:remove_from_wishlist", args=[self.book.pk]),
            {"csrfmiddlewaretoken": token}).status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(pk=item.pk).exists())

    @requirement("BOOK-SR-004", "BOOK-F-019")
    def test_seller_cannot_add_or_remove_buyer_wishlist_item(self):
        item = WishlistItem.objects.create(buyer=self.buyer, book=self.book)
        client, token = self.csrf_client(self.seller)
        for name in ("books:add_to_wishlist", "books:remove_from_wishlist"):
            response = client.post(reverse(name, args=[self.book.pk]), {"csrfmiddlewaretoken": token})
            self.assertRedirects(response, reverse("books:book_catalogue"), fetch_redirect_response=False)
        self.assertTrue(WishlistItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(WishlistItem.objects.filter(buyer=self.seller).exists())

    @requirement("BOOK-SR-004", "BOOK-F-019")
    def test_anonymous_wishlist_access_requires_login(self):
        response = self.client.get(reverse("books:wishlist"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("books:wishlist"),
                             fetch_redirect_response=False)

    @requirement("BOOK-SR-005", "BOOK-F-019")
    def test_get_requests_cannot_add_or_remove_wishlist_entries(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse("books:add_to_wishlist", args=[self.book.pk])).status_code, 302)
        self.assertFalse(WishlistItem.objects.exists())
        item = WishlistItem.objects.create(buyer=self.buyer, book=self.book)
        self.assertEqual(self.client.get(reverse("books:remove_from_wishlist", args=[self.book.pk])).status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(pk=item.pk).exists())

    def test_sql_like_search_is_literal_and_does_not_broaden_results(self):
        response = self.client.get(reverse("books:book_catalogue"), {"q": "' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["paginator"].count, 0)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(self.client.get(reverse("books:book_catalogue"),
            {"q": "Security Fixture"}).context["paginator"].count, 1)

    def test_sql_like_login_identifier_does_not_bypass_authentication(self):
        response = self.client.post(reverse("login"), {"username": "' OR 1=1 --", "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_search_reflection_escapes_html_attribute_payload(self):
        payload = '\"><script>alert("QA_SECURITY")</script>'
        response = self.client.get(reverse("books:book_catalogue"), {"q": payload})
        self.assertContains(response, escape(payload))
        self.assertNotContains(response, payload)

    def test_stored_book_title_is_escaped_in_catalogue_and_detail(self):
        payload = '<script>alert("QA_STORED_SECURITY")</script>'
        self.book.title = payload
        self.book.save(update_fields=["title"])
        for url in (reverse("books:book_catalogue"), reverse("books:book_detail", args=[self.book.pk])):
            response = self.client.get(url)
            self.assertContains(response, escape(payload))
            self.assertNotContains(response, payload)
