from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from books.models import Book

from .models import Cart, CartItem, ShippingAddress


class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user(
            username="testbuyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=cls.buyer,
            role=Profile.Role.BUYER,
        )

        cls.seller = User.objects.create_user(
            username="testseller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=cls.seller,
            role=Profile.Role.SELLER,
        )

        cls.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="9781234567890",
            description="A book for testing.",
            category="Testing",
            price=Decimal("250.00"),
            stock_quantity=5,
            is_available=True,
        )

        cls.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Another Author",
            isbn="9781234567891",
            price=Decimal("100.00"),
            stock_quantity=5,
            is_available=False,
        )

    def setUp(self):
        self.client.force_login(self.buyer)
        self.cart = Cart.objects.create(user=self.buyer)

    def test_buyer_can_view_empty_cart(self):
        response = self.client.get(reverse("cart:cart_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your cart is empty")

    def test_buyer_can_add_book_to_cart(self):
        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 2},
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        item = CartItem.objects.get(cart=self.cart, book=self.book)
        self.assertEqual(item.quantity, 2)

    def test_adding_same_book_increases_quantity(self):
        self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 1},
        )
        self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 2},
        )

        self.assertEqual(
            CartItem.objects.filter(cart=self.cart, book=self.book).count(),
            1,
        )
        self.assertEqual(
            CartItem.objects.get(cart=self.cart, book=self.book).quantity,
            3,
        )

    def test_cannot_add_more_than_available_stock(self):
        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 6},
        )

        self.assertRedirects(
            response,
            reverse("book_detail", args=[self.book.id]),
        )
        self.assertFalse(
            CartItem.objects.filter(cart=self.cart, book=self.book).exists()
        )

    def test_cannot_increase_existing_quantity_beyond_stock(self):
        CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=4,
        )

        self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 2},
        )

        item = CartItem.objects.get(cart=self.cart, book=self.book)
        self.assertEqual(item.quantity, 4)

    def test_cannot_add_unavailable_book(self):
        response = self.client.post(
            reverse(
                "cart:add_to_cart",
                args=[self.unavailable_book.id],
            ),
            {"quantity": 1},
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            CartItem.objects.filter(
                cart=self.cart,
                book=self.unavailable_book,
            ).exists()
        )

    def test_invalid_quantity_is_rejected(self):
        for quantity in ["0", "-1", "abc"]:
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    reverse("cart:add_to_cart", args=[self.book.id]),
                    {"quantity": quantity},
                )

                self.assertRedirects(
                    response,
                    reverse("book_detail", args=[self.book.id]),
                )

        self.assertFalse(
            CartItem.objects.filter(cart=self.cart, book=self.book).exists()
        )

    def test_buyer_can_update_quantity(self):
        item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=1,
        )

        response = self.client.post(
            reverse("cart:update_cart_item", args=[item.id]),
            {"quantity": 3},
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_cannot_update_quantity_beyond_stock(self):
        item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=2,
        )

        self.client.post(
            reverse("cart:update_cart_item", args=[item.id]),
            {"quantity": 6},
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_buyer_can_remove_item(self):
        item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=1,
        )

        response = self.client.post(
            reverse("cart:remove_from_cart", args=[item.id]),
        )

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_seller_cannot_access_cart(self):
        self.client.force_login(self.seller)

        response = self.client.get(reverse("cart:cart_detail"))

        self.assertRedirects(
            response,
            reverse("book_catalogue"),
        )

    def test_seller_cannot_add_book_to_cart(self):
        self.client.force_login(self.seller)

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id]),
            {"quantity": 1},
        )

        self.assertRedirects(
            response,
            reverse("book_catalogue"),
        )
        self.assertFalse(
            CartItem.objects.filter(book=self.book).exists()
        )

    def test_cart_totals_are_calculated_correctly(self):
        CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=3,
        )

        self.assertEqual(self.cart.total_items, 3)
        self.assertEqual(self.cart.total_price, Decimal("750.00"))

class CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user(
            username="checkoutbuyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=cls.buyer,
            role=Profile.Role.BUYER,
        )

        cls.other_buyer = User.objects.create_user(
            username="otherbuyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=cls.other_buyer,
            role=Profile.Role.BUYER,
        )

        cls.seller = User.objects.create_user(
            username="checkoutseller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=cls.seller,
            role=Profile.Role.SELLER,
        )

        cls.book = Book.objects.create(
            title="Checkout Test Book",
            author="Test Author",
            isbn="9781234567892",
            description="A book for checkout tests.",
            category="Testing",
            price=Decimal("300.00"),
            stock_quantity=10,
            is_available=True,
        )

    def setUp(self):
        self.client.force_login(self.buyer)
        self.cart = Cart.objects.create(user=self.buyer)
        self.item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=2,
        )

        self.address = ShippingAddress.objects.create(
            user=self.buyer,
            full_name="Test Buyer",
            address_line_1="123 Test Street",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            is_default=True,
        )

    def test_buyer_can_view_checkout(self):
        response = self.client.get(reverse("cart:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart/checkout.html")
        self.assertContains(response, "Checkout Test Book")

    def test_checkout_displays_saved_shipping_address(self):
        response = self.client.get(reverse("cart:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Buyer")
        self.assertContains(response, "Bengaluru")

    def test_empty_cart_cannot_proceed_to_checkout(self):
        self.item.delete()

        response = self.client.get(reverse("cart:checkout"))

        self.assertRedirects(
            response,
            reverse("cart:cart_detail"),
        )

    def test_seller_cannot_access_checkout(self):
        self.client.force_login(self.seller)

        response = self.client.get(reverse("cart:checkout"))

        self.assertRedirects(
            response,
            reverse("book_catalogue"),
        )

    def test_checkout_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse("cart:checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_valid_saved_address_and_payment_method_are_accepted(self):
        response = self.client.post(
            reverse("cart:checkout"),
            {
                "address_id": self.address.id,
                "payment_method": "TEST_CARD",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["checkout_pending"])
        self.assertEqual(
            response.context["selected_address"],
            self.address,
        )

        # Checkout validation must not remove items or charge the buyer.
        self.assertTrue(
            CartItem.objects.filter(
                cart=self.cart,
                book=self.book,
                quantity=2,
            ).exists()
        )

    def test_address_belonging_to_another_buyer_is_rejected(self):
        other_address = ShippingAddress.objects.create(
            user=self.other_buyer,
            full_name="Another Buyer",
            address_line_1="456 Other Street",
            city="Mysuru",
            state="Karnataka",
            postal_code="570001",
            country="India",
            phone_number="9876543211",
        )

        response = self.client.post(
            reverse("cart:checkout"),
            {
                "address_id": other_address.id,
                "payment_method": "TEST_CARD",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["checkout_pending"])
        self.assertFalse(
            response.context["checkout_form"].is_valid()
        )
        self.assertTrue(
            CartItem.objects.filter(
                cart=self.cart,
                book=self.book,
            ).exists()
        )

    def test_invalid_payment_method_is_rejected(self):
        response = self.client.post(
            reverse("cart:checkout"),
            {
                "address_id": self.address.id,
                "payment_method": "INVALID_METHOD",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["checkout_pending"])
        self.assertFalse(
            response.context["checkout_form"].is_valid()
        )

    def test_new_shipping_address_can_be_saved(self):
        response = self.client.post(
            reverse("cart:checkout"),
            {
                "use_new_address": "yes",
                "payment_method": "TEST_UPI",
                "full_name": "New Test Recipient",
                "address_line_1": "789 New Street",
                "address_line_2": "",
                "city": "Mangaluru",
                "state": "Karnataka",
                "postal_code": "575001",
                "country": "India",
                "phone_number": "9876543212",
                "is_default": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["checkout_pending"])

        new_address = ShippingAddress.objects.get(
            user=self.buyer,
            full_name="New Test Recipient",
        )

        self.assertEqual(new_address.city, "Mangaluru")
        self.assertTrue(new_address.is_default)

        # Saving checkout details must preserve the cart.
        self.assertTrue(
            CartItem.objects.filter(
                cart=self.cart,
                book=self.book,
            ).exists()
        )

        # Only one saved address should be the default.
        self.assertEqual(
            ShippingAddress.objects.filter(
                user=self.buyer,
                is_default=True,
            ).count(),
            1,
        )

    def test_invalid_new_shipping_address_is_not_saved(self):
        initial_address_count = ShippingAddress.objects.filter(
            user=self.buyer
        ).count()

        response = self.client.post(
            reverse("cart:checkout"),
            {
                "use_new_address": "yes",
                "payment_method": "TEST_CARD",
                "full_name": "Invalid Recipient",
                "address_line_1": "",
                "address_line_2": "",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India",
                "phone_number": "9876543210",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["checkout_pending"])
        self.assertEqual(
            ShippingAddress.objects.filter(
                user=self.buyer
            ).count(),
            initial_address_count,
        )

    def test_new_address_with_invalid_payment_method_is_not_saved(self):
        initial_address_count = ShippingAddress.objects.filter(
            user=self.buyer
        ).count()

        response = self.client.post(
            reverse("cart:checkout"),
            {
                "use_new_address": "yes",
                "payment_method": "INVALID_METHOD",
                "full_name": "New Recipient",
                "address_line_1": "10 Test Road",
                "address_line_2": "",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India",
                "phone_number": "9876543210",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["checkout_pending"])
        self.assertEqual(
            ShippingAddress.objects.filter(
                user=self.buyer
            ).count(),
            initial_address_count,
        )