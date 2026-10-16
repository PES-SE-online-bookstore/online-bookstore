from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings

from accounts.models import Profile
from books.models import Book
from orders.models import Order, OrderItem


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@onlinebookstore.local",
)
class OrderEmailNotificationTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username="notification_buyer",
            email="notification@example.com",
            password="TestPassword123!",
        )

        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.book = Book.objects.create(
            title="Notification Test Book",
            author="Test Author",
            isbn="9781234567892",
            description="A book used for email notification tests.",
            category="Testing",
            price=Decimal("250.00"),
            stock_quantity=10,
            is_available=True,
        )

        self.order = Order.objects.create(
            user=self.buyer,
            full_name="Notification Buyer",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            total_amount=Decimal("250.00"),
            status=Order.Status.PENDING,
        )

        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            book_title=self.book.title,
            unit_price=Decimal("250.00"),
            quantity=1,
        )

        mail.outbox.clear()

    def test_creating_pending_order_does_not_send_email(self):
        self.assertEqual(len(mail.outbox), 0)

    def test_confirmed_status_sends_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.CONFIRMED
            self.order.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ["notification@example.com"],
        )
        self.assertIn(
            "confirmed",
            mail.outbox[0].subject.lower(),
        )
        self.assertIn(
            f"#{self.order.pk}",
            mail.outbox[0].body,
        )

    def test_shipped_status_sends_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.SHIPPED
            self.order.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ["notification@example.com"],
        )
        self.assertIn(
            "shipped",
            mail.outbox[0].subject.lower(),
        )

    def test_delivered_status_sends_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.DELIVERED
            self.order.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ["notification@example.com"],
        )
        self.assertIn(
            "delivered",
            mail.outbox[0].subject.lower(),
        )

    def test_saving_without_status_change_does_not_send_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.full_name = "Updated Buyer Name"
            self.order.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_cancelled_status_does_not_send_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.CANCELLED
            self.order.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_email_failure_does_not_prevent_status_update(self):
        with self.assertLogs(
            "orders.email_notifications",
            level="ERROR",
        ):
            with patch(
                "orders.email_notifications.send_mail",
                side_effect=RuntimeError("Simulated email failure"),
            ):
                with self.captureOnCommitCallbacks(execute=True):
                    self.order.status = Order.Status.CONFIRMED
                    self.order.save()

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.CONFIRMED,
        )

    def test_email_contains_order_and_item_details(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.CONFIRMED
            self.order.save()

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertIn("Notification Buyer", email.body)
        self.assertIn("Notification Test Book", email.body)
        self.assertIn("250.00", email.body)
        self.assertIn("Bengaluru", email.body)

    def test_transition_from_confirmed_to_shipped_sends_new_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.CONFIRMED
            self.order.save()

        with self.captureOnCommitCallbacks(execute=True):
            self.order.status = Order.Status.SHIPPED
            self.order.save()

        self.assertEqual(len(mail.outbox), 2)

        self.assertIn(
            "confirmed",
            mail.outbox[0].subject.lower(),
        )
        self.assertIn(
            "shipped",
            mail.outbox[1].subject.lower(),
        )