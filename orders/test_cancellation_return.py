from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from orders.models import Order, ReturnRequest


User = get_user_model()


@override_settings(
    ORDER_CANCELLATION_WINDOW_DAYS=7,
    ORDER_RETURN_WINDOW_DAYS=7,
)
class OrderCancellationReturnTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username="cancel_return_buyer",
            email="cancel_return@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.other_buyer = User.objects.create_user(
            username="cancel_return_other",
            email="other_cancel_return@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.other_buyer,
            role=Profile.Role.BUYER,
        )

        self.client.force_login(self.buyer)

        self.order = self.create_order()

    def create_order(
        self,
        user=None,
        status=Order.Status.PENDING,
        created_at=None,
        delivered_at=None,
    ):
        order = Order.objects.create(
            user=user or self.buyer,
            full_name="Test Buyer",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            total_amount=Decimal("300.00"),
            status=status,
        )

        fields_to_update = []

        if created_at is not None:
            order.created_at = created_at
            fields_to_update.append("created_at")

        if delivered_at is not None:
            order.delivered_at = delivered_at
            fields_to_update.append("delivered_at")

        if fields_to_update:
            Order.objects.filter(pk=order.pk).update(
                **{
                    field: getattr(order, field)
                    for field in fields_to_update
                }
            )
            order.refresh_from_db()

        return order

    def test_buyer_can_cancel_pending_order(self):
        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.CANCELLED,
        )

    def test_buyer_can_cancel_confirmed_order(self):
        self.order.status = Order.Status.CONFIRMED
        self.order.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.CANCELLED,
        )

    def test_cancellation_is_rejected_after_policy_window(self):
        old_creation_time = timezone.now() - timedelta(days=8)

        Order.objects.filter(pk=self.order.pk).update(
            created_at=old_creation_time
        )

        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.PENDING,
        )

    def test_shipped_order_cannot_be_cancelled(self):
        self.order.status = Order.Status.SHIPPED
        self.order.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.SHIPPED,
        )

    def test_delivered_order_cannot_be_cancelled(self):
        self.order.status = Order.Status.DELIVERED
        self.order.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.DELIVERED,
        )

    def test_buyer_cannot_cancel_another_buyers_order(self):
        other_order = self.create_order(
            user=self.other_buyer,
        )

        response = self.client.post(
            reverse("orders:cancel", args=[other_order.pk])
        )

        self.assertEqual(response.status_code, 404)

        other_order.refresh_from_db()

        self.assertEqual(
            other_order.status,
            Order.Status.PENDING,
        )

    def test_anonymous_user_cannot_cancel_order(self):
        self.client.logout()

        response = self.client.post(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.PENDING,
        )

    def test_cancellation_endpoint_rejects_get(self):
        response = self.client.get(
            reverse("orders:cancel", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 405)

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.PENDING,
        )

    def test_buyer_can_request_return_for_delivered_order(self):
        delivery_time = timezone.now() - timedelta(days=1)

        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=delivery_time,
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "The book arrived damaged."},
        )

        self.assertEqual(response.status_code, 302)

        return_request = ReturnRequest.objects.get(
            order=delivered_order
        )

        self.assertEqual(return_request.buyer, self.buyer)
        self.assertEqual(
            return_request.reason,
            "The book arrived damaged.",
        )
        self.assertEqual(
            return_request.status,
            ReturnRequest.Status.PENDING,
        )

    def test_return_request_requires_a_reason(self):
        delivery_time = timezone.now() - timedelta(days=1)

        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=delivery_time,
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "   "},
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_return_request_rejects_reason_over_2000_characters(self):
        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=1),
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "A" * 2001},
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_return_request_rejected_for_undelivered_order(self):
        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[self.order.pk],
            ),
            {"reason": "I no longer need this book."},
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=self.order
            ).exists()
        )

    def test_return_request_rejected_after_policy_window(self):
        old_delivery_time = timezone.now() - timedelta(days=8)

        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=old_delivery_time,
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "The book is no longer needed."},
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_return_request_rejected_without_delivery_timestamp(self):
        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
        )

        # Simulate a legacy or inconsistent record with no delivery timestamp.
        # QuerySet.update() bypasses model save signals.
        Order.objects.filter(pk=delivered_order.pk).update(
            delivered_at=None
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "The book arrived damaged."},
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_duplicate_return_request_is_rejected(self):
        delivery_time = timezone.now() - timedelta(days=1)

        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=delivery_time,
        )

        ReturnRequest.objects.create(
            order=delivered_order,
            buyer=self.buyer,
            reason="The book arrived damaged.",
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "I want to submit another request."},
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).count(),
            1,
        )

    def test_buyer_cannot_request_return_for_another_buyers_order(self):
        delivered_order = self.create_order(
            user=self.other_buyer,
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=1),
        )

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "The book arrived damaged."},
        )

        self.assertEqual(response.status_code, 404)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_anonymous_user_cannot_request_return(self):
        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=1),
        )

        self.client.logout()

        response = self.client.post(
            reverse(
                "orders:request_return",
                args=[delivered_order.pk],
            ),
            {"reason": "The book arrived damaged."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

        self.assertFalse(
            ReturnRequest.objects.filter(
                order=delivered_order
            ).exists()
        )

    def test_return_endpoint_rejects_get(self):
        response = self.client.get(
            reverse(
                "orders:request_return",
                args=[self.order.pk],
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_order_detail_shows_cancellation_option_for_eligible_order(self):
        response = self.client.get(
            reverse("orders:detail", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancellation and Returns")
        self.assertContains(response, "Cancel Order")

    def test_order_detail_shows_return_request_status(self):
        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=1),
        )

        ReturnRequest.objects.create(
            order=delivered_order,
            buyer=self.buyer,
            reason="The book arrived damaged.",
        )

        response = self.client.get(
            reverse("orders:detail", args=[delivered_order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Return Request Status")
        self.assertContains(response, "Pending")
        self.assertContains(response, "The book arrived damaged.")

    def test_return_reason_html_is_escaped_on_order_detail_page(self):
        delivered_order = self.create_order(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=1),
        )

        malicious_reason = '<script>alert("xss")</script>'

        ReturnRequest.objects.create(
            order=delivered_order,
            buyer=self.buyer,
            reason=malicious_reason,
        )

        response = self.client.get(
            reverse("orders:detail", args=[delivered_order.pk])
        )

        self.assertEqual(response.status_code, 200)

        # The HTML must be displayed as escaped text.
        self.assertContains(
            response,
            "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;",
            html=False,
        )

        # The raw script element must not appear in the response.
        self.assertNotContains(
            response,
            malicious_reason,
            html=False,
        )