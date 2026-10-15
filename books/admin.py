from django.contrib import admin, messages

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "seller",
        "approval_status",
        "is_available",
        "price",
        "stock_quantity",
    )

    search_fields = (
        "title",
        "author",
        "isbn",
        "seller__username",
    )

    list_filter = (
        "approval_status",
        "is_available",
        "category",
    )

    ordering = ("title",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    actions = (
        "approve_listings",
        "reject_listings",
    )

    @admin.action(description="Approve selected seller listings")
    def approve_listings(self, request, queryset):
        approved_count = 0

        for book in queryset:
            book.approval_status = Book.ApprovalStatus.APPROVED

            # Approved books without stock remain unavailable.
            book.is_available = book.stock_quantity > 0

            book.save(
                update_fields=(
                    "approval_status",
                    "is_available",
                    "updated_at",
                )
            )

            approved_count += 1

        self.message_user(
            request,
            (
                f"{approved_count} listing(s) approved. "
                "Listings without stock remain unavailable."
            ),
            level=messages.SUCCESS,
        )

    @admin.action(description="Reject selected seller listings")
    def reject_listings(self, request, queryset):
        rejected_count = 0

        for book in queryset:
            book.approval_status = Book.ApprovalStatus.REJECTED
            book.is_available = False

            book.save(
                update_fields=(
                    "approval_status",
                    "is_available",
                    "updated_at",
                )
            )

            rejected_count += 1

        self.message_user(
            request,
            f"{rejected_count} listing(s) rejected and made unavailable.",
            level=messages.SUCCESS,
        )