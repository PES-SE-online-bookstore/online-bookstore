from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Profile
from books.models import Book
from cart.models import Cart, CartItem, ShippingAddress
from orders.models import Order, OrderItem, Payment
from orders.services import MockPaymentGateway, create_order_from_cart


class CreateOrderFromCartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer_test",
            email="buyer@example.com",
            password="TestPassword123!",
        )

        Profile.objects.create(
            user=self.user,
            role=Profile.Role.BUYER,
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="9781234567890",
            description="A book used for testing.",
            category="Testing",
            price=Decimal("250.00"),
            stock_quantity=10,
            is_available=True,
        )

        self.cart = Cart.objects.create(user=self.user)

        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=2,
        )

        self.address = ShippingAddress.objects.create(
            user=self.user,
            full_name="Test Buyer",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
        )

    def test_creates_order_items_and_pending_payment(self):
        order, payment = create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, Decimal("500.00"))
        self.assertEqual(order.status, Order.Status.PENDING)

        order_item = order.items.get()

        self.assertEqual(order_item.book, self.book)
        self.assertEqual(order_item.book_title, "Test Book")
        self.assertEqual(
            order_item.unit_price,
            Decimal("250.00"),
        )
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.subtotal, Decimal("500.00"))

        self.assertEqual(payment.order, order)
        self.assertEqual(payment.amount, Decimal("500.00"))
        self.assertEqual(payment.method, Payment.Method.TEST_CARD)
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_order_preserves_shipping_address_snapshot(self):
        order, _ = create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        self.address.full_name = "Updated Buyer Name"
        self.address.address_line_1 = "456 New Street"
        self.address.save()

        order.refresh_from_db()

        self.assertEqual(order.full_name, "Test Buyer")
        self.assertEqual(
            order.address_line_1,
            "123 Test Street",
        )

    def test_rejects_deleted_book(self):
        self.cart_item.delete()
        self.book.delete()

        with self.assertRaisesMessage(
            ValueError,
            "Cannot create an order from an empty cart.",
        ):
            create_order_from_cart(
                user=self.user,
                cart=self.cart,
                shipping_address=self.address,
                payment_method=Payment.Method.TEST_CARD,
            )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_rejects_invalid_payment_method(self):
        with self.assertRaisesMessage(
            ValueError,
            "Invalid payment method.",
        ):
            create_order_from_cart(
                user=self.user,
                cart=self.cart,
                shipping_address=self.address,
                payment_method="INVALID_METHOD",
            )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_rejects_unavailable_book(self):
        self.book.is_available = False
        self.book.save(update_fields=["is_available"])

        with self.assertRaisesMessage(
            ValueError,
            f'"{self.book.title}" is currently unavailable.',
        ):
            create_order_from_cart(
                user=self.user,
                cart=self.cart,
                shipping_address=self.address,
                payment_method=Payment.Method.TEST_CARD,
            )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_rejects_insufficient_stock(self):
        self.book.stock_quantity = 1
        self.book.save(update_fields=["stock_quantity"])

        with self.assertRaisesMessage(
            ValueError,
            f'Not enough stock available for "{self.book.title}".',
        ):
            create_order_from_cart(
                user=self.user,
                cart=self.cart,
                shipping_address=self.address,
                payment_method=Payment.Method.TEST_CARD,
            )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_order_creation_does_not_reduce_inventory(self):
        original_stock = self.book.stock_quantity

        create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        self.book.refresh_from_db()

        self.assertEqual(
            self.book.stock_quantity,
            original_stock,
        )

    def test_order_creation_does_not_clear_cart(self):
        create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        self.assertEqual(self.cart.items.count(), 1)

    @patch.object(
        MockPaymentGateway,
        "initiate_payment",
        return_value={
            "success": True,
            "payment_id": "1",
            "reference": "TEST-REFERENCE-123",
            "message": "Mock payment initiated.",
        },
    )
    def test_successful_initiation_keeps_payment_pending(
        self,
        mock_initiate,
    ):
        order, payment = create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        payment.refresh_from_db()
        order.refresh_from_db()

        mock_initiate.assert_called_once()

        self.assertEqual(
            payment.transaction_reference,
            "TEST-REFERENCE-123",
        )
        self.assertEqual(
            payment.status,
            Payment.Status.PENDING,
        )
        self.assertEqual(
            order.status,
            Order.Status.PENDING,
        )

    @patch.object(
        MockPaymentGateway,
        "initiate_payment",
        return_value={
            "success": False,
            "message": "Mock initiation failed.",
        },
    )
    def test_failed_initiation_marks_payment_failed(
        self,
        mock_initiate,
    ):
        order, payment = create_order_from_cart(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method=Payment.Method.TEST_CARD,
        )

        payment.refresh_from_db()
        order.refresh_from_db()

        mock_initiate.assert_called_once()

        self.assertEqual(
            payment.status,
            Payment.Status.FAILED,
        )
        self.assertEqual(
            payment.failure_reason,
            "Mock initiation failed.",
        )
        self.assertEqual(
            order.status,
            Order.Status.PENDING,
        )
        self.assertEqual(
            payment.transaction_reference,
            "",
        )


class OrderHistoryAndDetailTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username="history_buyer",
            email="history@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.other_buyer = User.objects.create_user(
            username="other_buyer",
            email="other@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.other_buyer,
            role=Profile.Role.BUYER,
        )

        self.book = Book.objects.create(
            title="Order History Book",
            author="Test Author",
            isbn="9781234567891",
            description="A book used to test order history.",
            category="Testing",
            price=Decimal("150.00"),
            stock_quantity=5,
            is_available=True,
        )

        self.order = Order.objects.create(
            user=self.buyer,
            full_name="History Buyer",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            total_amount=Decimal("300.00"),
            status=Order.Status.PENDING,
        )

        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            book_title=self.book.title,
            unit_price=Decimal("150.00"),
            quantity=2,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            method=Payment.Method.TEST_CARD,
            amount=Decimal("300.00"),
            status=Payment.Status.PENDING,
        )

    def test_buyer_can_view_order_history(self):
        self.client.force_login(self.buyer)

        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Orders")
        self.assertContains(response, f"#{self.order.pk}")
        self.assertContains(response, "Order History Book")

    def test_order_history_does_not_show_other_buyers_orders(self):
        Order.objects.create(
            user=self.other_buyer,
            full_name="Other Buyer",
            address_line_1="456 Other Street",
            address_line_2="",
            city="Mysuru",
            state="Karnataka",
            postal_code="570001",
            country="India",
            phone_number="9876543211",
            total_amount=Decimal("50.00"),
            status=Order.Status.PENDING,
        )

        self.client.force_login(self.buyer)

        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{self.order.pk}")
        self.assertNotContains(response, "Other Buyer")

    def test_buyer_can_view_own_order_details(self):
        self.client.force_login(self.buyer)

        response = self.client.get(f"/orders/{self.order.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order History Book")
        self.assertContains(response, "History Buyer")
        self.assertContains(response, "Test Card")
        self.assertContains(response, "Pending")

    def test_buyer_cannot_view_another_buyers_order(self):
        other_order = Order.objects.create(
            user=self.other_buyer,
            full_name="Other Buyer",
            address_line_1="456 Other Street",
            address_line_2="",
            city="Mysuru",
            state="Karnataka",
            postal_code="570001",
            country="India",
            phone_number="9876543211",
            total_amount=Decimal("50.00"),
            status=Order.Status.PENDING,
        )

        self.client.force_login(self.buyer)

        response = self.client.get(f"/orders/{other_order.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_order_history_requires_login(self):
        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_order_details_require_login(self):
        response = self.client.get(f"/orders/{self.order.pk}/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)
