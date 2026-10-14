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
            price="450.00",
            stock_quantity=10,
            is_available=True,
        )

        cls.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Test Author",
            isbn="9781234567890",
            description="This book is unavailable.",
            price="250.00",
            stock_quantity=0,
            is_available=False,
        )

    def test_catalogue_page_loads(self):
        response = self.client.get(reverse("book_catalogue"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/catalogue.html")

    def test_available_books_are_displayed(self):
        response = self.client.get(reverse("book_catalogue"))

        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Robert C. Martin")
        self.assertContains(response, "450.00")

    def test_unavailable_books_are_excluded(self):
        response = self.client.get(reverse("book_catalogue"))

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Unavailable Book")

    def test_search_by_title(self):
        response = self.client.get(
            reverse("book_catalogue"),
            {"q": "Clean Code"},
        )

        self.assertContains(response, "Clean Code")
        self.assertNotContains(response, "Unavailable Book")

    def test_search_by_author(self):
        response = self.client.get(
            reverse("book_catalogue"),
            {"q": "Robert C. Martin"},
        )

        self.assertContains(response, "Clean Code")

    def test_search_by_isbn(self):
        response = self.client.get(
            reverse("book_catalogue"),
            {"q": "9780132350884"},
        )

        self.assertContains(response, "Clean Code")

    def test_unmatched_search_displays_message(self):
        response = self.client.get(
            reverse("book_catalogue"),
            {"q": "Nonexistent Book XYZ"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No books found matching "Nonexistent Book XYZ".',
        )

    def test_empty_catalogue_displays_message(self):
        Book.objects.all().delete()

        response = self.client.get(reverse("book_catalogue"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No books are currently available in the catalogue.",
        )