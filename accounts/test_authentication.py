"""OBP-41: business validation and HTTP/database integration, not live browser tests.

SRS checks intentionally fail when email login or 30-minute token expiry is absent.
No expected-failure markers or production-setting overrides hide those defects.
"""

import re
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core import mail
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.forms import RegistrationForm
from accounts.models import LoginAttempt, Profile
from qa.catalog import requirement


User = get_user_model()
PASSWORD = "Bookstore-QA!9vL72"
NEW_PASSWORD = "Reset-Bookstore!8mK63"


def registration_data(**changes):
    return {"username": "qa_new_buyer", "email": "new@example.com", "password": PASSWORD,
            "confirm_password": PASSWORD, "role": "BUYER", **changes}


class RegistrationValidationUnitTests(SimpleTestCase):
    """Isolate the application form rules with the user lookup mocked."""
    qa_level = "Unit"
    qa_requirements = ("BOOK-F-001",)

    def validate(self, data, existing_field=None):
        def lookup(**kwargs):
            return SimpleNamespace(exists=lambda: existing_field in kwargs if existing_field else False)
        with patch("accounts.forms.User.objects.filter", side_effect=lookup):
            form = RegistrationForm(data)
            form.is_valid()
            return form

    def test_valid_registration_passes_validation(self):
        self.assertTrue(self.validate(registration_data()).is_valid())

    def test_email_is_normalized(self):
        form = self.validate(registration_data(email="  Mixed@Example.COM  "))
        self.assertEqual(form.cleaned_data["email"], "mixed@example.com")

    def test_username_is_trimmed(self):
        self.assertEqual(self.validate(registration_data(username="  qa_trimmed  ")).cleaned_data["username"], "qa_trimmed")

    def test_duplicate_email_is_rejected(self):
        self.assertIn("email", self.validate(registration_data(), "email__iexact").errors)

    def test_duplicate_username_is_rejected(self):
        self.assertIn("username", self.validate(registration_data(), "username__iexact").errors)

    def test_mismatched_password_is_rejected(self):
        self.assertIn("confirm_password", self.validate(registration_data(confirm_password=NEW_PASSWORD)).errors)

    def test_short_password_is_rejected(self):
        self.assertIn("password", self.validate(registration_data(password="aB!3", confirm_password="aB!3")).errors)

    def test_numeric_password_is_rejected(self):
        self.assertIn("password", self.validate(registration_data(password="8931750264", confirm_password="8931750264")).errors)

    def test_invalid_email_is_rejected(self):
        self.assertIn("email", self.validate(registration_data(email="invalid-address")).errors)

    @requirement("BOOK-F-001", "BOOK-SR-004")
    def test_admin_role_cannot_be_selected(self):
        self.assertIn("role", self.validate(registration_data(role="ADMIN")).errors)


class RegistrationIntegrationTests(TestCase):
    qa_level = "Integration"
    qa_requirements = ("BOOK-F-001",)

    def register(self, **changes):
        return self.client.post(reverse("register"), registration_data(**changes))

    def test_registration_page_loads(self):
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)

    def test_buyer_account_and_profile_are_created(self):
        response = self.register()
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        user = User.objects.get(username="qa_new_buyer")
        self.assertTrue(user.is_active)
        self.assertEqual(user.profile.role, Profile.Role.BUYER)

    def test_seller_account_and_profile_are_created(self):
        self.register(role="SELLER")
        self.assertEqual(User.objects.get(username="qa_new_buyer").profile.role, Profile.Role.SELLER)

    def test_duplicate_email_does_not_create_another_account(self):
        self.register()
        self.register(username="different", email="NEW@EXAMPLE.COM")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

    def test_duplicate_username_does_not_create_another_account(self):
        self.register()
        self.register(username="QA_NEW_BUYER", email="another@example.com")
        self.assertEqual(User.objects.count(), 1)

    def test_mismatched_password_creates_no_account_or_profile(self):
        self.register(confirm_password=NEW_PASSWORD)
        self.assertFalse(User.objects.exists())
        self.assertFalse(Profile.objects.exists())

    def test_missing_required_data_creates_no_account(self):
        self.client.post(reverse("register"), {})
        self.assertFalse(User.objects.exists())

    @requirement("BOOK-F-001", "BOOK-SR-002")
    def test_registration_stores_verifiable_hash_not_plaintext(self):
        self.register()
        user = User.objects.get(username="qa_new_buyer")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.check_password(NEW_PASSWORD))
        self.assertIn(identify_hasher(user.password).algorithm, {"pbkdf2_sha256", "argon2"})

    @requirement("BOOK-F-001", "BOOK-SR-004")
    def test_registration_cannot_create_an_admin(self):
        self.register(role="ADMIN", is_staff="true", is_superuser="true")
        self.assertFalse(User.objects.exists())


class AuthenticationFixture(TestCase):
    qa_level = "Integration"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="qa_buyer", email="buyer@example.com", password=PASSWORD)
        Profile.objects.create(user=cls.user, role=Profile.Role.BUYER)

    def login(self, username="qa_buyer", password=PASSWORD):
        return self.client.post(reverse("login"), {"username": username, "password": password})


class LoginIntegrationTests(AuthenticationFixture):
    qa_requirements = ("BOOK-F-002",)

    def test_login_page_loads(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)

    def test_current_username_login_establishes_session(self):
        """Characterization of current username interface; not proof of email-login acceptance."""
        self.login()
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_srs_email_and_password_establish_session(self):
        """BOOK-F-002 requires email login; do not weaken to username login."""
        self.login(username=self.user.email)
        self.assertIn("_auth_user_id", self.client.session, "SRS email login did not establish a session")

    def test_wrong_password_does_not_establish_session(self):
        self.login(password=NEW_PASSWORD)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_account_does_not_create_attempt_record(self):
        self.login(username="does_not_exist")
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(LoginAttempt.objects.exists())

    def test_missing_credentials_are_rejected(self):
        response = self.client.post(reverse("login"), {})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    @requirement("BOOK-F-002", "BOOK-F-017")
    def test_inactive_account_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.login()
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_wrong_password_can_be_followed_by_successful_login(self):
        self.login(password=NEW_PASSWORD)
        self.login()
        self.assertIn("_auth_user_id", self.client.session)
        self.assertFalse(LoginAttempt.objects.filter(user=self.user).exists())


class LockoutIntegrationTests(AuthenticationFixture):
    qa_requirements = ("BOOK-F-003", "BOOK-SR-005")

    def fail_attempts(self, count):
        for _ in range(count):
            self.login(password=NEW_PASSWORD)

    def test_first_failure_is_counted(self):
        self.fail_attempts(1)
        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertEqual(attempt.failed_attempts, 1)
        self.assertIsNone(attempt.locked_until)

    def test_four_failures_do_not_lock_account(self):
        self.fail_attempts(4)
        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertEqual(attempt.failed_attempts, 4)
        self.assertIsNone(attempt.locked_until)

    def test_fifth_failure_locks_for_fifteen_minutes(self):
        now = timezone.now()
        with patch("accounts.views.timezone.now", return_value=now):
            self.fail_attempts(5)
        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertEqual(attempt.failed_attempts, 5)
        self.assertEqual(attempt.locked_until, now + timedelta(minutes=15))

    def test_correct_password_is_blocked_during_lockout(self):
        self.fail_attempts(5)
        self.login()
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_sixth_attempt_shows_lockout_message(self):
        self.fail_attempts(5)
        response = self.login(password=NEW_PASSWORD)
        self.assertContains(response, "temporarily unavailable")
        self.assertEqual(LoginAttempt.objects.get(user=self.user).failed_attempts, 5)

    def test_correct_password_works_after_expiry(self):
        self.fail_attempts(5)
        deadline = LoginAttempt.objects.get(user=self.user).locked_until
        with patch("accounts.views.timezone.now", return_value=deadline + timedelta(seconds=1)):
            self.login()
        self.assertIn("_auth_user_id", self.client.session)
        self.assertFalse(LoginAttempt.objects.filter(user=self.user).exists())

    def test_wrong_password_after_expiry_starts_new_count(self):
        self.fail_attempts(5)
        deadline = LoginAttempt.objects.get(user=self.user).locked_until
        with patch("accounts.views.timezone.now", return_value=deadline + timedelta(seconds=1)):
            self.login(password=NEW_PASSWORD)
        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertEqual(attempt.failed_attempts, 1)
        self.assertIsNone(attempt.locked_until)

    def test_success_between_failures_resets_consecutive_count(self):
        self.fail_attempts(4)
        self.login()
        self.client.post(reverse("logout"))
        self.fail_attempts(1)
        self.assertEqual(LoginAttempt.objects.get(user=self.user).failed_attempts, 1)

    def test_another_account_is_not_locked(self):
        other = User.objects.create_user(username="other_buyer", password=PASSWORD)
        self.fail_attempts(5)
        self.login(username=other.username)
        self.assertEqual(int(self.client.session["_auth_user_id"]), other.pk)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetIntegrationTests(AuthenticationFixture):
    qa_requirements = ("BOOK-F-004",)
    clock = datetime(2026, 11, 2, 12, 0, 0)

    def request_link(self, email="buyer@example.com"):
        with patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now", return_value=self.clock):
            response = self.client.post(reverse("password_reset"), {"email": email})
        self.assertEqual(response.status_code, 302)
        return response

    def link(self):
        self.request_link()
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r"/accounts/reset/[^/\s]+/[^/\s]+/", mail.outbox[0].body)
        self.assertIsNotNone(match, "Reset message does not contain a reset URL")
        return match.group(0)

    def open_link(self, link, seconds=0):
        with patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now",
                   return_value=self.clock + timedelta(seconds=seconds)):
            return self.client.get(link, follow=True)

    def change_password(self):
        response = self.open_link(self.link())
        self.assertTrue(response.context["validlink"])
        confirmation_url = response.redirect_chain[-1][0]
        with patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now", return_value=self.clock):
            return self.client.post(confirmation_url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})

    def test_reset_request_page_loads(self):
        self.assertEqual(self.client.get(reverse("password_reset")).status_code, 200)

    def test_registered_account_receives_reset_message(self):
        self.request_link()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["buyer@example.com"])

    def test_unknown_email_discloses_no_account_and_sends_no_message(self):
        response = self.request_link("unknown@example.com")
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.url, reverse("password_reset_done"))

    def test_inactive_account_receives_no_reset_message(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.request_link()
        self.assertEqual(len(mail.outbox), 0)

    def test_link_is_valid_before_thirty_minutes(self):
        response = self.open_link(self.link(), seconds=1799)
        self.assertTrue(response.context["validlink"])

    def test_srs_link_expires_after_thirty_minutes(self):
        """BOOK-F-004: no timeout override; verify actual application configuration."""
        response = self.open_link(self.link(), seconds=1801)
        self.assertFalse(response.context["validlink"], "Reset link remains usable after the SRS 30-minute expiry")

    def test_tampered_token_is_rejected(self):
        link = self.link()
        response = self.open_link(link[:-2] + "x/")
        self.assertFalse(response.context["validlink"])

    def test_successful_reset_changes_password(self):
        response = self.change_password()
        self.assertRedirects(response, reverse("password_reset_complete"), fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    def test_used_link_cannot_be_reused(self):
        link = self.link()
        response = self.open_link(link)
        with patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now", return_value=self.clock):
            self.client.post(response.redirect_chain[-1][0], {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})
        self.assertFalse(self.open_link(link).context["validlink"])

    def test_mismatched_reset_passwords_do_not_change_password(self):
        response = self.open_link(self.link())
        with patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now", return_value=self.clock):
            result = self.client.post(response.redirect_chain[-1][0], {"new_password1": NEW_PASSWORD, "new_password2": PASSWORD})
        self.assertEqual(result.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    @requirement("BOOK-F-004", "BOOK-F-002")
    def test_new_password_logs_in_and_old_password_does_not(self):
        self.change_password()
        self.login(password=PASSWORD)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.login(password=NEW_PASSWORD)
        self.assertIn("_auth_user_id", self.client.session)


class SessionAccessIntegrationTests(AuthenticationFixture):
    qa_requirements = ("BOOK-F-002", "BOOK-SR-004")

    def test_anonymous_cart_access_redirects_to_login(self):
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_logged_in_buyer_can_access_cart(self):
        self.login()
        self.assertEqual(self.client.get(reverse("cart:cart_detail")).status_code, 200)

    def test_post_logout_removes_authentication(self):
        self.login()
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_access_after_logout_is_denied(self):
        self.login()
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("cart:cart_detail")).status_code, 302)

    def test_get_logout_does_not_change_session(self):
        self.login()
        self.client.get(reverse("logout"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_independent_client_has_no_authenticated_session(self):
        self.login()
        other = Client()
        self.assertNotIn("_auth_user_id", other.session)
        self.assertEqual(other.get(reverse("cart:cart_detail")).status_code, 302)

    @requirement("BOOK-SR-005")
    def test_login_post_without_csrf_token_is_rejected(self):
        response = Client(enforce_csrf_checks=True).post(reverse("login"), {"username": self.user.username, "password": PASSWORD})
        self.assertEqual(response.status_code, 403)

    @requirement("BOOK-SR-005")
    def test_logout_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse("logout")).status_code, 403)
        self.assertIn("_auth_user_id", client.session)
