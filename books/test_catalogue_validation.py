"""OBP-42 integration gaps: pagination, moderation visibility and SRS fields."""

from decimal import Decimal
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book, Review
from qa.catalog import requirement


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            self.links.append(href)


class CataloguePaginationIntegrationTests(TestCase):
    qa_level = "Integration"
    qa_requirements = ("BOOK-F-005",)

    @classmethod
    def setUpTestData(cls):
        Book.objects.bulk_create([
            Book(title=f"QA Pagination {n:02}", author="QA Author", isbn=f"97800000{n:05}",
                 description="Pagination fixture", category="QA & Programming", price=Decimal("200.00"),
                 stock_quantity=5, is_available=True, approval_status=Book.ApprovalStatus.APPROVED)
            for n in range(25)
        ])

    def page(self, **params):
        return self.client.get(reverse("books:book_catalogue"), params)

    def test_first_page_contains_twelve_books(self):
        response = self.page()
        self.assertEqual(len(response.context["books"]), 12)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertEqual(response.context["paginator"].count, 25)

    def test_three_pages_do_not_omit_or_repeat_books(self):
        pages = [[book.pk for book in self.page(page=n).context["books"]] for n in (1, 2, 3)]
        self.assertEqual([len(page) for page in pages], [12, 12, 1])
        flattened = [pk for page in pages for pk in page]
        self.assertEqual(len(set(flattened)), 25)
        self.assertEqual(set(flattened), set(Book.objects.values_list("pk", flat=True)))

    def test_invalid_page_input_falls_back_without_error(self):
        response = self.page(page="not-a-page")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)

    def test_out_of_range_page_resolves_to_last_page(self):
        response = self.page(page=999)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 3)

    @requirement("BOOK-F-005", "BOOK-F-006")
    def test_pagination_links_preserve_encoded_search_and_filters(self):
        response = self.page(q="QA Pagination", category="QA & Programming", min_price="200", max_price="200")
        parser = LinkParser()
        parser.feed(response.content.decode())
        next_links = [link for link in parser.links if parse_qs(urlsplit(link).query).get("page") == ["2"]]
        self.assertTrue(next_links)
        self.assertEqual(parse_qs(urlsplit(next_links[0]).query), {
            "q": ["QA Pagination"], "category": ["QA & Programming"],
            "min_price": ["200"], "max_price": ["200"], "page": ["2"],
        })


class CatalogueVisibilityIntegrationTests(TestCase):
    qa_level = "Integration"
    qa_requirements = ("BOOK-F-005", "BOOK-F-016")

    @classmethod
    def setUpTestData(cls):
        cls.pending = Book.objects.create(title="QA Pending", author="QA", isbn="9780000000901",
                                         price="200", stock_quantity=5, is_available=True,
                                         category="QA Pending Only", approval_status=Book.ApprovalStatus.PENDING)
        cls.rejected = Book.objects.create(title="QA Rejected", author="QA", isbn="9780000000902",
                                          price="200", stock_quantity=5, is_available=True,
                                          category="QA Rejected Only", approval_status=Book.ApprovalStatus.REJECTED)
        cls.approved = Book.objects.create(title="QA Approved", author="QA", isbn="9780000000903",
                                          price="200", stock_quantity=5, is_available=True,
                                          category="QA Approved Category", approval_status=Book.ApprovalStatus.APPROVED)

    def test_unapproved_books_and_their_categories_are_hidden(self):
        response = self.client.get(reverse("books:book_catalogue"))
        self.assertEqual(list(response.context["books"]), [self.approved])
        self.assertEqual(list(response.context["categories"]), ["QA Approved Category"])

    @requirement("BOOK-F-007", "BOOK-F-016")
    def test_pending_book_is_inaccessible_by_direct_url(self):
        self.assertEqual(self.client.get(reverse("books:book_detail", args=[self.pending.pk])).status_code, 404)

    @requirement("BOOK-F-007", "BOOK-F-016")
    def test_rejected_book_is_inaccessible_by_direct_url(self):
        self.assertEqual(self.client.get(reverse("books:book_detail", args=[self.rejected.pk])).status_code, 404)


class CatalogueRequiredFieldsIntegrationTests(TestCase):
    qa_level = "Integration"

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.seller = user_model.objects.create_user(username="qa_visible_seller")
        cls.book = Book.objects.create(title="QA Required Fields", author="QA Author", isbn="9780000000910",
                                       seller=cls.seller, price="200", stock_quantity=5,
                                       description="QA description", cover_image_url="https://example.com/qa-cover.png",
                                       is_available=True, approval_status=Book.ApprovalStatus.APPROVED)

    @requirement("BOOK-F-005")
    def test_srs_catalogue_renders_book_cover_image(self):
        """BOOK-F-005 requires cover image in the catalogue, not only detail page."""
        response = self.client.get(reverse("books:book_catalogue"))
        self.assertContains(response, f'src="{self.book.cover_image_url}"')

    @requirement("BOOK-F-007")
    def test_srs_book_detail_identifies_seller(self):
        response = self.client.get(reverse("books:book_detail", args=[self.book.pk]))
        self.assertContains(response, self.seller.username)

    @requirement("BOOK-F-007")
    def test_book_detail_displays_computed_average_rating(self):
        user_model = get_user_model()
        for n, rating in enumerate((3, 5)):
            buyer = user_model.objects.create_user(username=f"qa_rating_buyer_{n}")
            Review.objects.create(book=self.book, buyer=buyer, rating=rating, comment="QA averaging fixture")
        response = self.client.get(reverse("books:book_detail", args=[self.book.pk]))
        self.assertEqual(response.context["average_rating"], 4)
        self.assertEqual(response.context["review_count"], 2)
        self.assertContains(response, "4.0 / 5")
