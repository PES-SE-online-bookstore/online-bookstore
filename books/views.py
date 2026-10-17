from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order, OrderItem

from .forms import BookListingForm, ReviewForm
from .models import Book, Review, WishlistItem


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

    # Sort results consistently before pagination.
    books = books.order_by("title", "id")

    # Display at most 12 books per page.
    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

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
        "books": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
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

    reviews = (
        Review.objects.filter(book=book)
        .select_related("buyer")
        .order_by("-created_at")
    )

    review_stats = reviews.aggregate(
        average_rating=Avg("rating"),
    )

    review_form = None
    can_review = False
    has_reviewed = False
    is_in_wishlist = False

    if request.user.is_authenticated:
        # Only users with a Buyer profile may submit reviews.
        is_buyer = (
            hasattr(request.user, "profile")
            and request.user.profile.role == "BUYER"
        )

        if is_buyer:
            has_reviewed = Review.objects.filter(
                book=book,
                buyer=request.user,
            ).exists()

            has_purchased = OrderItem.objects.filter(
                book=book,
                order__user=request.user,
            ).exclude(
                order__status=Order.Status.CANCELLED,
            ).exists()

            can_review = has_purchased and not has_reviewed

            if can_review:
                review_form = ReviewForm()

        # Only buyers can have wishlist items.
        if is_buyer:
            is_in_wishlist = WishlistItem.objects.filter(
                buyer=request.user,
                book=book,
            ).exists()

    context = {
        "book": book,
        "reviews": reviews,
        "average_rating": review_stats["average_rating"],
        "review_count": reviews.count(),
        "review_form": review_form,
        "can_review": can_review,
        "has_reviewed": has_reviewed,
        "is_in_wishlist": is_in_wishlist,
    }

    return render(request, "books/book_detail.html", context)


@login_required
def submit_review(request, book_id):
    if request.method != "POST":
        return redirect("books:book_detail", book_id=book_id)

    book = get_object_or_404(
        Book,
        id=book_id,
        is_available=True,
        approval_status=Book.ApprovalStatus.APPROVED,
    )

    # Only users with a Buyer profile may submit reviews.
    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "BUYER"
    ):
        messages.error(
            request,
            "Only buyers can submit book reviews.",
        )
        return redirect("books:book_detail", book_id=book.pk)

    # Only buyers with a non-cancelled order containing this book may review.
    has_purchased = OrderItem.objects.filter(
        book=book,
        order__user=request.user,
    ).exclude(
        order__status=Order.Status.CANCELLED,
    ).exists()

    if not has_purchased:
        messages.error(
            request,
            "You must purchase this book before reviewing it.",
        )
        return redirect("books:book_detail", book_id=book.pk)

    if Review.objects.filter(book=book, buyer=request.user).exists():
        messages.error(
            request,
            "You have already reviewed this book.",
        )
        return redirect("books:book_detail", book_id=book.pk)

    form = ReviewForm(request.POST)

    if not form.is_valid():
        # Keep validation errors visible on the book details page.
        reviews = (
            Review.objects.filter(book=book)
            .select_related("buyer")
            .order_by("-created_at")
        )

        review_stats = reviews.aggregate(
            average_rating=Avg("rating"),
        )

        is_in_wishlist = WishlistItem.objects.filter(
            buyer=request.user,
            book=book,
        ).exists()

        context = {
            "book": book,
            "reviews": reviews,
            "average_rating": review_stats["average_rating"],
            "review_count": reviews.count(),
            "review_form": form,
            "can_review": True,
            "has_reviewed": False,
            "is_in_wishlist": is_in_wishlist,
        }

        return render(
            request,
            "books/book_detail.html",
            context,
            status=400,
        )

    try:
        with transaction.atomic():
            # The database constraint also prevents duplicate reviews.
            Review.objects.create(
                book=book,
                buyer=request.user,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )

    except Exception:
        # A concurrent duplicate submission may violate the unique constraint.
        if Review.objects.filter(book=book, buyer=request.user).exists():
            messages.error(
                request,
                "You have already reviewed this book.",
            )
        else:
            raise

        return redirect("books:book_detail", book_id=book.pk)

    messages.success(request, "Your review was submitted successfully.")
    return redirect("books:book_detail", book_id=book.pk)


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


@login_required
def my_listings(request):
    # Only sellers may manage book listings.
    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "SELLER":
        messages.error(request, "Only sellers can manage book listings.")
        return redirect("books:book_catalogue")

    listings = Book.objects.filter(
        seller=request.user,
    ).order_by("-created_at")

    return render(
        request,
        "books/my_listings.html",
        {"listings": listings},
    )


@login_required
def edit_listing(request, book_id):
    # Only sellers may edit listings.
    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "SELLER":
        messages.error(request, "Only sellers can edit book listings.")
        return redirect("books:book_catalogue")

    # Restrict access to listings owned by the logged-in seller.
    book = get_object_or_404(
        Book,
        id=book_id,
        seller=request.user,
    )

    if request.method == "POST":
        form = BookListingForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save(commit=False)

            # Editing a listing requires fresh admin approval.
            book.approval_status = Book.ApprovalStatus.PENDING
            book.is_available = False
            book.save()

            messages.success(
                request,
                "Your listing was updated and submitted for admin approval.",
            )
            return redirect("books:my_listings")

    else:
        form = BookListingForm(instance=book)

    return render(
        request,
        "books/edit_listing.html",
        {
            "form": form,
            "book": book,
        },
    )


@login_required
def delete_listing(request, book_id):
    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "SELLER":
        messages.error(request, "Only sellers can delete book listings.")
        return redirect("books:book_catalogue")

    book = get_object_or_404(
        Book,
        id=book_id,
        seller=request.user,
    )

    if request.method == "POST":
        try:
            with transaction.atomic():
                book.delete()

            messages.success(
                request,
                "Your book listing was deleted successfully.",
            )

        except ProtectedError:
            messages.error(
                request,
                "This listing cannot be deleted because it is "
                "associated with existing orders.",
            )

        return redirect("books:my_listings")

    return render(
        request,
        "books/confirm_delete_listing.html",
        {"book": book},
    )


@login_required
def wishlist(request):
    """Display the logged-in buyer's saved books."""
    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "BUYER":
        messages.error(request, "Only buyers can manage a wishlist.")
        return redirect("books:book_catalogue")

    wishlist_items = (
        WishlistItem.objects.filter(buyer=request.user)
        .select_related("book")
        .order_by("-created_at")
    )

    return render(
        request,
        "books/wishlist.html",
        {"wishlist_items": wishlist_items},
    )


@login_required
def add_to_wishlist(request, book_id):
    """Add an approved, available book to the buyer's wishlist."""
    if request.method != "POST":
        return redirect("books:book_detail", book_id=book_id)

    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "BUYER":
        messages.error(request, "Only buyers can manage a wishlist.")
        return redirect("books:book_catalogue")

    book = get_object_or_404(
        Book,
        id=book_id,
        is_available=True,
        approval_status=Book.ApprovalStatus.APPROVED,
    )

    _, created = WishlistItem.objects.get_or_create(
        buyer=request.user,
        book=book,
    )

    if created:
        messages.success(
            request,
            f'"{book.title}" was added to your wishlist.',
        )
    else:
        messages.info(
            request,
            f'"{book.title}" is already in your wishlist.',
        )

    return redirect("books:book_detail", book_id=book.pk)


@login_required
def remove_from_wishlist(request, book_id):
    """Remove a saved book belonging to the logged-in buyer."""
    if request.method != "POST":
        return redirect("books:wishlist")

    if not hasattr(request.user, "profile"):
        messages.error(request, "Your account profile was not found.")
        return redirect("books:book_catalogue")

    if request.user.profile.role != "BUYER":
        messages.error(request, "Only buyers can manage a wishlist.")
        return redirect("books:book_catalogue")

    item = WishlistItem.objects.filter(
        buyer=request.user,
        book_id=book_id,
    ).first()

    if item is None:
        messages.info(request, "That book is not in your wishlist.")
    else:
        book_title = item.book.title
        item.delete()
        messages.success(
            request,
            f'"{book_title}" was removed from your wishlist.',
        )

    return redirect("books:wishlist")