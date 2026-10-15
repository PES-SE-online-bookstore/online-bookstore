from django.contrib import admin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "book",
        "book_title",
        "unit_price",
        "quantity",
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "full_name", "phone_number")
    readonly_fields = (
        "user",
        "total_amount",
        "full_name",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
        "phone_number",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "method",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "method", "created_at")
    search_fields = ("id", "order__id", "transaction_reference")
    readonly_fields = (
        "order",
        "method",
        "amount",
        "status",
        "transaction_reference",
        "failure_reason",
        "created_at",
        "updated_at",
    )