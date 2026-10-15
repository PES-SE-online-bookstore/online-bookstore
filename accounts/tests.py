from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AdminAccountManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username="account_admin",
            email="account_admin@example.com",
            password="TestAdminPassword123!",
        )

        cls.regular_user = User.objects.create_user(
            username="account_customer",
            email="customer@example.com",
            password="TestCustomerPassword123!",
        )

    def setUp(self):
        self.client.force_login(self.admin_user)
        self.changelist_url = reverse("admin:auth_user_changelist")

    def run_admin_action(self, action, user_ids):
        return self.client.post(
            self.changelist_url,
            {
                "action": action,
                "index": "0",
                "_selected_action": [
                    str(user_id) for user_id in user_ids
                ],
            },
            follow=True,
        )

    def test_admin_can_deactivate_account(self):
        response = self.run_admin_action(
            "deactivate_accounts",
            [self.regular_user.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_admin_can_reactivate_account(self):
        self.regular_user.is_active = False
        self.regular_user.save(update_fields=["is_active"])

        response = self.run_admin_action(
            "activate_accounts",
            [self.regular_user.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_active)

    def test_admin_cannot_deactivate_own_account(self):
        response = self.run_admin_action(
            "deactivate_accounts",
            [self.admin_user.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)

    def test_admin_can_deactivate_other_account_without_deactivating_self(self):
        response = self.run_admin_action(
            "deactivate_accounts",
            [self.admin_user.pk, self.regular_user.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.admin_user.refresh_from_db()
        self.regular_user.refresh_from_db()

        self.assertTrue(self.admin_user.is_active)
        self.assertFalse(self.regular_user.is_active)

    def test_deactivated_user_cannot_authenticate(self):
        self.regular_user.is_active = False
        self.regular_user.save(update_fields=["is_active"])

        user = User.objects.get(username="account_customer")

        from django.contrib.auth import authenticate

        authenticated_user = authenticate(
            username="account_customer",
            password="TestCustomerPassword123!",
        )

        self.assertIsNone(authenticated_user)

    def test_deactivated_user_cannot_log_in(self):
        self.regular_user.is_active = False
        self.regular_user.save(update_fields=["is_active"])

        self.client.logout()

        response = self.client.post(
            reverse("login"),
            {
                "username": "account_customer",
                "password": "TestCustomerPassword123!",
            },
            follow=True,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_non_staff_user_cannot_access_user_admin(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 302)

    def test_account_admin_is_registered_with_custom_admin(self):
        registered_admin = admin.site._registry[User]

        self.assertEqual(
            registered_admin.__class__.__name__,
            "ManagedUserAdmin",
        )