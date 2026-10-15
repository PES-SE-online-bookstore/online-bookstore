from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookListingForm
from .models import Book


def book_catalogue(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    min_price_input = request.GET.get("min_price", "").strip()
    max_price_input = request.GET.get("max_price", "").strip()

    books = Book.objects.filter(
        is_available=True,
        approval_status=Book.ApprovalStatus.APPROVED,
    )

    # Search by title, author, ISBN, or individual description keywords.
    if query:
        search_terms = query.split()

        for term in search_terms:
            books = books.filter(
                Q(title__icontains=term)
                | Q(author__icontains=term)
                | Q(isbn__icontains=term)
                | Q(description__icontains=term)
            )

    # Filter by category.
    if category:
        books = books.filter(category__iexact=category)

    # Validate the minimum and maximum prices.
    min_price = None
    max_price = None
    price_error = ""

    if min_price_input:
        try:
            min_price = Decimal(min_price_input)

            if not min_price.is_finite() or min_price < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            min_price = None
            price_error = "Enter a valid, non-negative minimum price."

    if max_price_input:
        try:
            max_price = Decimal(max_price_input)

            if not max_price.is_finite() or max_price < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            max_price = None
            price_error = "Enter a valid, non-negative maximum price."

    # Reject a price range where the minimum exceeds the maximum.
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        price_error = "Minimum price cannot exceed maximum price."
        min_price = None
        max_price = None

    # Apply valid price filters.
    if min_price is not None:
        books = books.filter(price__gte=min_price)

    if max_price is not None:
        books = books.filter(price__lte=max_price)

    # Sort results alphabetically by title.
    books = books.order_by("title")

    # Retrieve categories available in the approved catalogue.
    categories = (
        Book.objects.filter(
            is_available=True,
            approval_status=Book.ApprovalStatus.APPROVED,
        )
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    context = {
        "books": books,
        "query": query,
        "category": category,
        "categories": categories,
        "min_price": min_price_input,
        "max_price": max_price_input,
        "price_error": price_error,
    }

    return render(request, "books/catalogue.html", context)


def book_detail(request, book_id):
    # Only display approved books that are available in the catalogue.
    book = get_object_or_404(
        Book,
        id=book_id,
        is_available=True,
        approval_status=Book.ApprovalStatus.APPROVED,
    )

    context = {
        "book": book,
    }

    return render(request, "books/book_detail.html", context)


@login_required
def create_listing(request):
    # Only sellers may create listings.
    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "SELLER":
        messages.error(request, "Only sellers can create book listings.")
        return redirect("books:book_catalogue")

    if request.method == "POST":
        form = BookListingForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)
            book.seller = request.user
            book.approval_status = Book.ApprovalStatus.PENDING
            book.is_available = False
            book.save()

            messages.success(
                request,
                "Your book listing was submitted for admin approval.",
            )
            return redirect("books:book_catalogue")
    else:
        form = BookListingForm()

    return render(
        request,
        "books/create_listing.html",
        {"form": form},
    )