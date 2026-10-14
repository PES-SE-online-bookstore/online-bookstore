from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "price",
        "stock_quantity",
        "is_available",
    )
    search_fields = ("title", "author", "isbn")
    list_filter = ("is_available",)
    ordering = ("title",)