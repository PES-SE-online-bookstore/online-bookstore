from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from books.models import Book

from .models import Cart, CartItem


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