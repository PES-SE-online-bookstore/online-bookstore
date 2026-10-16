from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order


User = get_user_model()


class ShipmentTrackingTests(TestCase):
    """Tests for the shipment tracking timeline on order details."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="tracking_buyer",
            email="tracking@example.com",
            password="TestPassword123!",
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name="Tracking Buyer",
            phone_number="9876543210",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            total_amount="500.00",
            status=Order.Status.PENDING,
        )

        self.client.force_login(self.user)

        self.url = reverse(
            "orders:detail",
            kwargs={"order_id": self.order.pk},
        )

    def get_order_page(self):
        return self.client.get(self.url)

    def test_pending_order_shows_order_received_as_current(self):
        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipment Tracking")
        self.assertContains(response, "Order Received")
        self.assertContains(response, "Current status:")
        self.assertContains(response, "Pending")

    def test_confirmed_order_shows_confirmed_status(self):
        self.order.status = Order.Status.CONFIRMED
        self.order.save()

        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmed", count=3)

    def test_processing_order_shows_processing_status(self):
        self.order.status = Order.Status.PROCESSING
        self.order.save()

        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Processing")
        self.assertContains(response, "Current status:")

    def test_shipped_order_shows_shipped_status(self):
        self.order.status = Order.Status.SHIPPED
        self.order.save()

        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipped")
        self.assertContains(response, "Current status:")

    def test_delivered_order_shows_delivered_status(self):
        self.order.status = Order.Status.DELIVERED
        self.order.save()

        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delivered")
        self.assertContains(response, "Current status:")

    def test_cancelled_order_shows_cancellation_message(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save()

        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order Cancelled")
        self.assertContains(
            response,
            "This order has been cancelled.",
        )

    def test_tracking_page_explains_live_courier_tracking_is_unavailable(self):
        response = self.get_order_page()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Live courier location and carrier tracking are not available.",
        )