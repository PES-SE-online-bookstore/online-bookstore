from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from books.models import Book, Review
from orders.models import Order, OrderItem


class ReviewRolePermissionTests(TestCase):
    """Verify that only eligible Buyers can submit book reviews."""

    def setUp(self):
        self.buyer = User.objects.create_user(
            username="rbac_buyer",
            email="buyer@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.seller = User.objects.create_user(
            username="rbac_seller",
            email="seller@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.seller,
            role=Profile.Role.SELLER,
        )

        self.user_without_profile = User.objects.create_user(
            username="rbac_no_profile",
            email="no-profile@example.com",
            password="TestPassword123!",
        )

        self.book = Book.objects.create(
            seller=self.seller,
            title="RBAC Test Book",
            author="Test Author",
            isbn="9781234567897",
            description="A book for testing role permissions.",
            category="Testing",
            price="499.00",
            stock_quantity=10,
            approval_status=Book.ApprovalStatus.APPROVED,
            is_available=True,
        )

        self.review_url = reverse(
            "books:submit_review",
            kwargs={"book_id": self.book.pk},
        )

        self.detail_url = reverse(
            "books:book_detail",
            kwargs={"book_id": self.book.pk},
        )

    def create_order_with_book(self, user):
        """Create an order containing the book for the given user."""
        order = Order.objects.create(
            user=user,
            full_name="Test Customer",
            address_line_1="123 Test Street",
            address_line_2="",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            total_amount=self.book.price,
            status=Order.Status.CONFIRMED,
        )

        OrderItem.objects.create(
            order=order,
            book=self.book,
            book_title=self.book.title,
            unit_price=self.book.price,
            quantity=1,
        )

        return order

    def test_buyer_with_purchase_can_submit_review(self):
        """An eligible Buyer should be allowed to review a purchased book."""
        self.create_order_with_book(self.buyer)
        self.client.force_login(self.buyer)

        response = self.client.post(
            self.review_url,
            {
                "rating": 5,
                "comment": "Excellent book!",
            },
        )

        self.assertRedirects(response, self.detail_url)
        self.assertTrue(
            Review.objects.filter(
                book=self.book,
                buyer=self.buyer,
            ).exists()
        )

    def test_seller_cannot_submit_review_even_after_purchase(self):
        """A Seller must not review a book even if they purchased it."""
        self.create_order_with_book(self.seller)
        self.client.force_login(self.seller)

        response = self.client.post(
            self.review_url,
            {
                "rating": 5,
                "comment": "Seller review attempt.",
            },
        )

        self.assertRedirects(response, self.detail_url)
        self.assertFalse(
            Review.objects.filter(
                book=self.book,
                buyer=self.seller,
            ).exists()
        )

    def test_user_without_profile_cannot_submit_review(self):
        """An authenticated user without a role profile must be rejected."""
        self.create_order_with_book(self.user_without_profile)
        self.client.force_login(self.user_without_profile)

        response = self.client.post(
            self.review_url,
            {
                "rating": 4,
                "comment": "Review attempt without a profile.",
            },
        )

        self.assertRedirects(response, self.detail_url)
        self.assertFalse(
            Review.objects.filter(
                book=self.book,
                buyer=self.user_without_profile,
            ).exists()
        )

    def test_seller_does_not_see_review_form_on_book_details(self):
        """The book-details page must not offer reviews to Sellers."""
        self.create_order_with_book(self.seller)
        self.client.force_login(self.seller)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_review"])
        self.assertIsNone(response.context["review_form"])

    def test_buyer_with_purchase_sees_review_form(self):
        """An eligible Buyer should see the review form."""
        self.create_order_with_book(self.buyer)
        self.client.force_login(self.buyer)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["can_review"])
        self.assertIsNotNone(response.context["review_form"])

    def test_anonymous_user_must_log_in_to_submit_review(self):
        """Anonymous users must be redirected to the login page."""
        response = self.client.post(
            self.review_url,
            {
                "rating": 5,
                "comment": "Anonymous review attempt.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
        self.assertEqual(Review.objects.filter(book=self.book).count(), 0)