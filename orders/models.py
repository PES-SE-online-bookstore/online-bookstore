from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    # Shipping address snapshot: preserves the address used for this order.
    full_name = models.CharField(max_length=150)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    book = models.ForeignKey(
        "books.Book",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    # Preserve the title and price as they were when ordered.
    book_title = models.CharField(max_length=255)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "book"],
                name="unique_book_per_order",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="order_item_quantity_gte_1",
            ),
        ]

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.book_title} x {self.quantity}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    class Method(models.TextChoices):
        TEST_CARD = "TEST_CARD", "Test Card"
        TEST_UPI = "TEST_UPI", "Test UPI"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    method = models.CharField(
        max_length=20,
        choices=Method.choices,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    failure_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.pk} - {self.status}"