from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from accounts.models import Profile
from .models import Book
from orders.models import Order, OrderItem


class BookCatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            description="A guide to writing clean code.",
            category="Programming",
            price="450.00",
            stock_quantity=10,
            is_available=True,
        )

        cls.python_book = Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            isbn="9781593279288",
            description="A hands-on introduction to Python programming.",
            category="Programming",
            price="350.00",
            stock_quantity=5,
            is_available=True,
        )

        cls.cheap_book = Book.objects.create(
            title="The Alchemist",
            author="Paulo Coelho",
            isbn="9780062315007",
            description="A novel about following your dreams.",
            category="Fiction",
            price="200.00",
            stock_quantity=8,
            is_available=True,
        )

        cls.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Test Author",
            isbn="9781234567890",
            description="This book is unavailable.",
            category="Programming",
            price="250.00",
            stock_quantity=0,
            is_available=False,
        )

    def test_catalogue_page_loads(self):
        response = self.client.get(reverse("books:book_catalogue"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/catalogue.html")

    def test_available_books_are_displayed(self):
        response = self.client.get(reverse("books:book_catalogue"))

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Robert C. Martin")
        self.assertContains(response, "450.00")
        self.assertContains(response, "Programming")

    def test_unavailable_books_are_excluded(self):
        response = self.client.get(reverse("books:book_catalogue"))

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Unavailable Book")

    def test_search_by_title(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "Clean Code"},
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Python Crash Course")

    def test_search_by_author(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "Robert C. Martin"},
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Python Crash Course")

    def test_search_by_isbn(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "9780132350884"},
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Python Crash Course")

    def test_search_by_description_keyword(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "introduction"},
        )

        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "Clean Code")

    def test_search_is_case_insensitive(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "CLEAN CODE"},
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Python Crash Course")

    def test_unmatched_search_displays_message(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"q": "Nonexistent Book XYZ"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No books match your search and filters.",
        )

    def test_empty_catalogue_displays_message(self):
        Book.objects.all().delete()

        response = self.client.get(reverse("books:book_catalogue"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No books match your search and filters.",
        )

    def test_filter_by_category(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"category": "Programming"},
        )

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "The Alchemist")

    def test_category_filter_is_case_insensitive(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"category": "programming"},
        )

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "The Alchemist")

    def test_category_filter_excludes_unavailable_books(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"category": "Programming"},
        )

        self.assertNotContains(response, "Unavailable Book")

    def test_filter_by_minimum_price(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"min_price": "350"},
        )

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "The Alchemist")

    def test_filter_by_maximum_price(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"max_price": "350"},
        )

        self.assertContains(response, "Python Crash Course")
        self.assertContains(response, "The Alchemist")
        self.assertNotContains(response, "Clean Code")

    def test_filter_by_price_range(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {
                "min_price": "300",
                "max_price": "400",
            },
        )

        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "Clean Code")
        self.assertNotContains(response, "The Alchemist")

    def test_price_boundaries_are_inclusive(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {
                "min_price": "350",
                "max_price": "350",
            },
        )

        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "Clean Code")
        self.assertNotContains(response, "The Alchemist")

    def test_filter_by_category_and_price_together(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {
                "category": "Programming",
                "min_price": "400",
            },
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Python Crash Course")
        self.assertNotContains(response, "The Alchemist")

    def test_search_and_filters_work_together(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {
                "q": "programming",
                "category": "Programming",
                "max_price": "400",
            },
        )

        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "Clean Code")
        self.assertNotContains(response, "The Alchemist")

    def test_invalid_minimum_price_does_not_crash(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"min_price": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Enter a valid, non-negative minimum price.",
        )

    def test_negative_minimum_price_is_rejected(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"min_price": "-10"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Enter a valid, non-negative minimum price.",
        )

    def test_invalid_maximum_price_does_not_crash(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"max_price": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Enter a valid, non-negative maximum price.",
        )

    def test_non_finite_price_is_rejected(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {"min_price": "NaN"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Enter a valid, non-negative minimum price.",
        )

    def test_minimum_price_greater_than_maximum_is_rejected(self):
        response = self.client.get(
            reverse("books:book_catalogue"),
            {
                "min_price": "500",
                "max_price": "100",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Minimum price cannot exceed maximum price.",
        )
        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Python Crash Course")
        self.assertContains(response, "The Alchemist")

    def test_results_are_ordered_by_title(self):
        response = self.client.get(reverse("books:book_catalogue"))

        books = list(response.context["books"])

        self.assertEqual(
            [book.title for book in books],
            [
                "Clean Code",
                "Python Crash Course",
                "The Alchemist",
            ],
        )


class BookDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            description="A practical guide to writing clean code.",
            category="Programming",
            price="450.00",
            stock_quantity=10,
            cover_image_url="https://example.com/clean-code.jpg",
            is_available=True,
        )

        cls.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Test Author",
            isbn="9781234567890",
            description="This book is unavailable.",
            category="Programming",
            price="250.00",
            stock_quantity=0,
            is_available=False,
        )

    def test_book_detail_page_loads(self):
        response = self.client.get(
            reverse("books:book_detail", args=[self.book.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/book_detail.html")

    def test_book_detail_displays_book_information(self):
        response = self.client.get(
            reverse("books:book_detail", args=[self.book.id])
        )

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Robert C. Martin")
        self.assertContains(response, "9780132350884")
        self.assertContains(response, "Programming")
        self.assertContains(
            response,
            "A practical guide to writing clean code.",
        )
        self.assertContains(response, "450.00")
        self.assertContains(response, "10 available")

    def test_book_detail_displays_cover_image(self):
        response = self.client.get(
            reverse("books:book_detail", args=[self.book.id])
        )

        self.assertContains(
            response,
            "https://example.com/clean-code.jpg",
        )
        self.assertContains(response, "Cover of Clean Code")

    def test_book_detail_shows_placeholder_without_cover_image(self):
        book_without_cover = Book.objects.create(
            title="Book Without Cover",
            author="Test Author",
            isbn="9781234567891",
            description="A book without a cover image.",
            category="Fiction",
            price="100.00",
            stock_quantity=2,
            is_available=True,
        )

        response = self.client.get(
            reverse("books:book_detail", args=[book_without_cover.id])
        )

        self.assertContains(response, "No cover image available")

    def test_book_detail_returns_404_for_nonexistent_book(self):
        response = self.client.get(
            reverse("books:book_detail", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

    def test_unavailable_book_detail_returns_404(self):
        response = self.client.get(
            reverse("books:book_detail", args=[self.unavailable_book.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_catalogue_links_to_book_details(self):
        response = self.client.get(reverse("books:book_catalogue"))

        self.assertContains(
            response,
            reverse("books:book_detail", args=[self.book.id]),
        )


class SellerCreateListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seller = User.objects.create_user(
            username="test_seller",
            password="TestSellerPass123!",
        )
        Profile.objects.create(
            user=cls.seller,
            role=Profile.Role.SELLER,
        )

        cls.buyer = User.objects.create_user(
            username="test_buyer",
            password="TestBuyerPass123!",
        )
        Profile.objects.create(
            user=cls.buyer,
            role=Profile.Role.BUYER,
        )

        cls.valid_listing_data = {
            "title": "Test Seller Book",
            "author": "Test Author",
            "isbn": "9781234567897",
            "description": "A test book listing.",
            "category": "Programming",
            "price": "299.99",
            "stock_quantity": "5",
            "cover_image_url": "https://example.com/test-book.jpg",
        }

    def test_seller_can_access_listing_form(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse("books:create_listing"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/create_listing.html")

    def test_seller_can_create_pending_listing(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:create_listing"),
            self.valid_listing_data,
        )

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )

        book = Book.objects.get(isbn="9781234567897")
        self.assertEqual(book.seller, self.seller)
        self.assertEqual(
            book.approval_status,
            Book.ApprovalStatus.PENDING,
        )
        self.assertFalse(book.is_available)

    def test_buyer_cannot_access_listing_form(self):
        self.client.force_login(self.buyer)
        response = self.client.get(reverse("books:create_listing"))

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )

    def test_buyer_cannot_create_listing(self):
        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse("books:create_listing"),
            self.valid_listing_data,
        )

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )
        self.assertFalse(
            Book.objects.filter(isbn="9781234567897").exists()
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("books:create_listing"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_invalid_isbn_is_rejected(self):
        self.client.force_login(self.seller)
        data = self.valid_listing_data.copy()
        data["isbn"] = "invalid-isbn"

        response = self.client.post(
            reverse("books:create_listing"),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "isbn",
            "Enter a valid ISBN containing 10 or 13 digits.",
        )

    def test_zero_price_is_rejected(self):
        self.client.force_login(self.seller)
        data = self.valid_listing_data.copy()
        data["price"] = "0"

        response = self.client.post(
            reverse("books:create_listing"),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "price",
            "Price must be greater than zero.",
        )

    def test_duplicate_isbn_is_rejected(self):
        Book.objects.create(
            title="Existing Book",
            author="Existing Author",
            isbn="9781234567897",
            price="100.00",
            stock_quantity=1,
        )

        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:create_listing"),
            self.valid_listing_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Book.objects.filter(title="Test Seller Book").exists()
        )


class SellerMyListingsTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="mylistings_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.seller,
            role=Profile.Role.SELLER,
        )

        self.buyer = User.objects.create_user(
            username="mylistings_buyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.pending_book = Book.objects.create(
            seller=self.seller,
            title="Pending Seller Book",
            author="Test Author",
            isbn="9781234567897",
            description="A pending listing.",
            category="Technology",
            price="250.00",
            stock_quantity=5,
            approval_status=Book.ApprovalStatus.PENDING,
            is_available=False,
        )

        self.approved_book = Book.objects.create(
            seller=self.seller,
            title="Approved Seller Book",
            author="Test Author",
            isbn="9781234567880",
            description="An approved listing.",
            category="Technology",
            price="350.00",
            stock_quantity=3,
            approval_status=Book.ApprovalStatus.APPROVED,
            is_available=True,
        )

        self.other_seller_book = Book.objects.create(
            title="Another Seller Book",
            author="Other Author",
            isbn="9781234567873",
            price="150.00",
            stock_quantity=2,
        )

    def test_seller_can_view_own_listings(self):
        self.client.login(
            username="mylistings_seller",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("books:my_listings")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "books/my_listings.html",
        )
        self.assertContains(response, "Pending Seller Book")
        self.assertContains(response, "Approved Seller Book")
        self.assertNotContains(response, "Another Seller Book")

    def test_seller_sees_approval_statuses(self):
        self.client.login(
            username="mylistings_seller",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("books:my_listings")
        )

        self.assertContains(response, "Pending Approval")
        self.assertContains(response, "Approved")

    def test_buyer_cannot_view_seller_listings(self):
        self.client.login(
            username="mylistings_buyer",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("books:my_listings")
        )

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("books:my_listings")
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('books:my_listings')}",
        )

    def test_seller_with_no_listings_sees_empty_state(self):
        empty_seller = User.objects.create_user(
            username="empty_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=empty_seller,
            role=Profile.Role.SELLER,
        )

        self.client.login(
            username="empty_seller",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("books:my_listings")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "You haven't created any book listings yet.",
        )

class SellerEditListingTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="edit_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.seller,
            role=Profile.Role.SELLER,
        )

        self.other_seller = User.objects.create_user(
            username="other_edit_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.other_seller,
            role=Profile.Role.SELLER,
        )

        self.buyer = User.objects.create_user(
            username="edit_buyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.book = Book.objects.create(
            seller=self.seller,
            title="Original Book",
            author="Original Author",
            isbn="9781234567897",
            description="Original description",
            category="Programming",
            price="500.00",
            stock_quantity=10,
            approval_status=Book.ApprovalStatus.APPROVED,
            is_available=True,
        )

        self.url = reverse(
            "books:edit_listing",
            args=[self.book.id],
        )

    def test_seller_can_open_edit_page(self):
        self.client.login(
            username="edit_seller",
            password="TestPassword123!",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Original Book")

    def test_seller_can_edit_own_listing(self):
        self.client.login(
            username="edit_seller",
            password="TestPassword123!",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Updated Book",
                "author": "Updated Author",
                "isbn": "9781234567804",
                "description": "Updated description",
                "category": "Technology",
                "price": "650.00",
                "stock_quantity": 15,
                "cover_image_url": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("books:my_listings"),
        )

        self.book.refresh_from_db()

        self.assertEqual(self.book.title, "Updated Book")
        self.assertEqual(self.book.author, "Updated Author")
        self.assertEqual(self.book.price, Decimal("650.00"))
        self.assertEqual(self.book.stock_quantity, 15)
        self.assertEqual(
            self.book.approval_status,
            Book.ApprovalStatus.PENDING,
        )
        self.assertFalse(self.book.is_available)

    def test_invalid_edit_does_not_change_listing(self):
        self.client.login(
            username="edit_seller",
            password="TestPassword123!",
        )

        response = self.client.post(
            self.url,
            {
                "title": "",
                "author": "Updated Author",
                "isbn": "9781234567804",
                "description": "",
                "category": "Technology",
                "price": "650.00",
                "stock_quantity": 15,
                "cover_image_url": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.book.refresh_from_db()

        self.assertEqual(self.book.title, "Original Book")
        self.assertEqual(
            self.book.approval_status,
            Book.ApprovalStatus.APPROVED,
        )
        self.assertTrue(self.book.is_available)

    def test_seller_cannot_edit_another_sellers_listing(self):
        self.client.login(
            username="other_edit_seller",
            password="TestPassword123!",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_buyer_cannot_edit_listing(self):
        self.client.login(
            username="edit_buyer",
            password="TestPassword123!",
        )

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.url}",
        )

class SellerDeleteListingTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="delete_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.seller,
            role=Profile.Role.SELLER,
        )

        self.other_seller = User.objects.create_user(
            username="other_delete_seller",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.other_seller,
            role=Profile.Role.SELLER,
        )

        self.buyer = User.objects.create_user(
            username="delete_buyer",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.buyer,
            role=Profile.Role.BUYER,
        )

        self.book = Book.objects.create(
            seller=self.seller,
            title="Book to Delete",
            author="Test Author",
            isbn="9781234567811",
            description="Test description",
            category="Programming",
            price="500.00",
            stock_quantity=10,
            approval_status=Book.ApprovalStatus.PENDING,
            is_available=False,
        )

        self.url = reverse(
            "books:delete_listing",
            args=[self.book.id],
        )

    def test_seller_can_open_delete_confirmation(self):
        self.client.login(
            username="delete_seller",
            password="TestPassword123!",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Book to Delete")

        self.book.refresh_from_db()
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_seller_can_delete_own_listing(self):
        self.client.login(
            username="delete_seller",
            password="TestPassword123!",
        )

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("books:my_listings"),
        )
        self.assertFalse(
            Book.objects.filter(pk=self.book.pk).exists()
        )

    def test_seller_cannot_delete_another_sellers_listing(self):
        self.client.login(
            username="other_delete_seller",
            password="TestPassword123!",
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Book.objects.filter(pk=self.book.pk).exists()
        )

    def test_buyer_cannot_delete_listing(self):
        self.client.login(
            username="delete_buyer",
            password="TestPassword123!",
        )

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("books:book_catalogue"),
        )
        self.assertTrue(
            Book.objects.filter(pk=self.book.pk).exists()
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.url}",
        )
        self.assertTrue(
            Book.objects.filter(pk=self.book.pk).exists()
        )

    def test_ordered_book_cannot_be_deleted(self):
        self.client.login(
            username="delete_seller",
            password="TestPassword123!",
        )

        order = Order.objects.create(
            user=self.buyer,
            full_name="Test Buyer",
            address_line_1="123 Test Street",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            phone_number="9876543210",
            total_amount=Decimal("500.00"),
        )

        order_item = OrderItem.objects.create(
            order=order,
            book=self.book,
            book_title=self.book.title,
            unit_price=self.book.price,
            quantity=1,
        )

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(
            response,
            reverse("books:my_listings"),
        )

        self.assertTrue(
            Book.objects.filter(pk=self.book.pk).exists()
        )

        self.assertTrue(
            OrderItem.objects.filter(pk=order_item.pk).exists()
        )

        self.assertContains(response, "cannot be deleted")

class AdminListingApprovalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username="listing_admin",
            email="listing_admin@example.com",
            password="TestAdminPassword123!",
        )

        cls.seller = User.objects.create_user(
            username="approval_seller",
            password="TestSellerPassword123!",
        )

        Profile.objects.create(
            user=cls.seller,
            role=Profile.Role.SELLER,
        )

        cls.pending_book = Book.objects.create(
            seller=cls.seller,
            title="Pending Approval Book",
            author="Approval Author",
            isbn="9781234567828",
            description="A listing waiting for approval.",
            category="Technology",
            price="300.00",
            stock_quantity=5,
            approval_status=Book.ApprovalStatus.PENDING,
            is_available=False,
        )

        cls.pending_out_of_stock_book = Book.objects.create(
            seller=cls.seller,
            title="Pending Out of Stock Book",
            author="Approval Author",
            isbn="9781234567835",
            description="A listing without stock.",
            category="Technology",
            price="200.00",
            stock_quantity=0,
            approval_status=Book.ApprovalStatus.PENDING,
            is_available=False,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)
        self.changelist_url = reverse("admin:books_book_changelist")

    def run_admin_action(self, action, book_ids):
        data = {
            "action": action,
            "index": "0",
            "_selected_action": [
                str(book_id) for book_id in book_ids
            ],
        }

        return self.client.post(
            self.changelist_url,
            data,
            follow=True,
        )

    def test_admin_can_open_book_listing_management(self):
        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Approval Book")

    def test_admin_can_approve_pending_listing(self):
        response = self.run_admin_action(
            "approve_listings",
            [self.pending_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.pending_book.refresh_from_db()

        self.assertEqual(
            self.pending_book.approval_status,
            Book.ApprovalStatus.APPROVED,
        )
        self.assertTrue(self.pending_book.is_available)
        self.assertContains(response, "1 listing(s) approved")

    def test_approved_listing_appears_in_public_catalogue(self):
        self.run_admin_action(
            "approve_listings",
            [self.pending_book.pk],
        )

        response = self.client.get(
            reverse("books:book_catalogue"),
        )

        self.assertContains(response, "Pending Approval Book")

    def test_admin_can_reject_pending_listing(self):
        response = self.run_admin_action(
            "reject_listings",
            [self.pending_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.pending_book.refresh_from_db()

        self.assertEqual(
            self.pending_book.approval_status,
            Book.ApprovalStatus.REJECTED,
        )
        self.assertFalse(self.pending_book.is_available)
        self.assertContains(response, "1 listing(s) rejected")

    def test_rejected_listing_does_not_appear_in_public_catalogue(self):
        self.run_admin_action(
            "reject_listings",
            [self.pending_book.pk],
        )

        response = self.client.get(
            reverse("books:book_catalogue"),
        )

        self.assertNotContains(response, "Pending Approval Book")

    def test_approved_listing_without_stock_remains_unavailable(self):
        self.run_admin_action(
            "approve_listings",
            [self.pending_out_of_stock_book.pk],
        )

        self.pending_out_of_stock_book.refresh_from_db()

        self.assertEqual(
            self.pending_out_of_stock_book.approval_status,
            Book.ApprovalStatus.APPROVED,
        )
        self.assertFalse(
            self.pending_out_of_stock_book.is_available,
        )

    def test_non_staff_user_cannot_access_admin_listing_management(self):
        buyer = User.objects.create_user(
            username="nonstaff_buyer",
            password="TestBuyerPassword123!",
        )

        Profile.objects.create(
            user=buyer,
            role=Profile.Role.BUYER,
        )

        self.client.force_login(buyer)

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 302)

        self.pending_book.refresh_from_db()

        self.assertEqual(
            self.pending_book.approval_status,
            Book.ApprovalStatus.PENDING,
        )

    def test_anonymous_user_cannot_access_admin_listing_management(self):
        self.client.logout()

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

class AdminInventoryManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username="inventory_admin",
            email="inventory_admin@example.com",
            password="TestAdminPassword123!",
        )

        cls.seller = User.objects.create_user(
            username="inventory_seller",
            password="TestSellerPassword123!",
        )

        Profile.objects.create(
            user=cls.seller,
            role=Profile.Role.SELLER,
        )

        cls.approved_book = Book.objects.create(
            seller=cls.seller,
            title="Inventory Test Book",
            author="Inventory Author",
            isbn="9781234567842",
            description="A book for inventory management tests.",
            category="Technology",
            price="400.00",
            stock_quantity=5,
            approval_status=Book.ApprovalStatus.APPROVED,
            is_available=True,
        )

        cls.pending_book = Book.objects.create(
            seller=cls.seller,
            title="Pending Inventory Book",
            author="Inventory Author",
            isbn="9781234567859",
            description="A book awaiting approval.",
            category="Technology",
            price="300.00",
            stock_quantity=5,
            approval_status=Book.ApprovalStatus.PENDING,
            is_available=False,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)
        self.changelist_url = reverse("admin:books_book_changelist")

    def run_admin_action(self, action, book_ids):
        return self.client.post(
            self.changelist_url,
            {
                "action": action,
                "index": "0",
                "_selected_action": [
                    str(book_id) for book_id in book_ids
                ],
            },
            follow=True,
        )

    def test_admin_can_update_stock_quantity(self):
        response = self.client.post(
            reverse(
                "admin:books_book_change",
                args=[self.approved_book.pk],
            ),
            {
                "title": self.approved_book.title,
                "author": self.approved_book.author,
                "isbn": self.approved_book.isbn,
                "description": self.approved_book.description,
                "category": self.approved_book.category,
                "price": str(self.approved_book.price),
                "stock_quantity": "20",
                "cover_image_url": self.approved_book.cover_image_url,
                "seller": str(self.seller.pk),
                "approval_status": Book.ApprovalStatus.APPROVED,
                "is_available": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.approved_book.refresh_from_db()
        self.assertEqual(self.approved_book.stock_quantity, 20)

    def test_admin_can_deactivate_listing(self):
        response = self.run_admin_action(
            "deactivate_listings",
            [self.approved_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.approved_book.refresh_from_db()
        self.assertFalse(self.approved_book.is_available)

    def test_deactivated_listing_is_hidden_from_catalogue(self):
        self.run_admin_action(
            "deactivate_listings",
            [self.approved_book.pk],
        )

        response = self.client.get(
            reverse("books:book_catalogue"),
        )

        self.assertNotContains(response, "Inventory Test Book")

    def test_admin_can_reactivate_approved_listing_with_stock(self):
        self.approved_book.is_available = False
        self.approved_book.save(update_fields=["is_available"])

        response = self.run_admin_action(
            "activate_listings",
            [self.approved_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.approved_book.refresh_from_db()
        self.assertTrue(self.approved_book.is_available)

    def test_pending_listing_cannot_be_activated(self):
        response = self.run_admin_action(
            "activate_listings",
            [self.pending_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.pending_book.refresh_from_db()
        self.assertFalse(self.pending_book.is_available)
        self.assertEqual(
            self.pending_book.approval_status,
            Book.ApprovalStatus.PENDING,
        )

    def test_out_of_stock_listing_cannot_be_activated(self):
        self.approved_book.stock_quantity = 0
        self.approved_book.is_available = False
        self.approved_book.save(
            update_fields=["stock_quantity", "is_available"]
        )

        response = self.run_admin_action(
            "activate_listings",
            [self.approved_book.pk],
        )

        self.assertEqual(response.status_code, 200)

        self.approved_book.refresh_from_db()
        self.assertFalse(self.approved_book.is_available)

    def test_non_staff_user_cannot_manage_inventory(self):
        buyer = User.objects.create_user(
            username="inventory_buyer",
            password="TestBuyerPassword123!",
        )

        Profile.objects.create(
            user=buyer,
            role=Profile.Role.BUYER,
        )

        self.client.force_login(buyer)

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 302)

        self.approved_book.refresh_from_db()
        self.assertEqual(self.approved_book.stock_quantity, 5)