from django.db.models import Q
from django.shortcuts import render

from .models import Book


def book_catalogue(request):
    query = request.GET.get("q", "").strip()

    books = Book.objects.filter(is_available=True)

    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(isbn__icontains=query)
        )

    books = books.order_by("title")

    context = {
        "books": books,
        "query": query,
    }

    return render(request, "books/catalogue.html", context)