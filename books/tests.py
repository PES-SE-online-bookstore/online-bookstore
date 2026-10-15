from django.test import TestCase
from django.urls import reverse

from .models import Book


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
