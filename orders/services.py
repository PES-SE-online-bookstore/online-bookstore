from decimal import Decimal
from uuid import uuid4

from django.db import transaction

from books.models import Book
from orders.models import Order, OrderItem, Payment


class MockPaymentGateway:
    """
    Simulates payment initiation for development and automated tests.

    This is NOT a real payment processor.
    It does not charge money or verify that a payment was completed.
    """

    @staticmethod
    def initiate_payment(payment):
        return {
            "success": True,
            "payment_id": str(payment.pk),
            "reference": f"TEST-{uuid4().hex[:16].upper()}",
            "message": "Mock payment initiated. No real money was charged.",
        }


@transaction.atomic
def create_order_from_cart(user, cart, shipping_address, payment_method):
    """
    Create a pending order and payment record from the user's cart.

    The mock gateway simulates payment initiation only. Payment remains
    pending until genuine payment verification is implemented.

    Inventory is not reduced, and the cart is not cleared here.
    """

    # Validate that the cart contains items.
    if not cart.items.exists():
        raise ValueError("Cannot create an order from an empty cart.")

    # Validate the selected payment method.
    if payment_method not in Payment.Method.values:
        raise ValueError("Invalid payment method.")

    # Retrieve cart items and lock the associated books to reduce
    # the risk of concurrent orders exceeding available stock.
    cart_items = list(
        cart.items.select_related("book").order_by("book_id")
    )

    book_ids = [item.book_id for item in cart_items]

    locked_books = {
        book.pk: book
        for book in (
            Book.objects.select_for_update()
            .filter(pk__in=book_ids)
            .order_by("pk")
        )
    }

    total_amount = Decimal("0.00")
    order_lines = []

    # Validate each item and calculate the order total.
    for item in cart_items:
        book = locked_books.get(item.book_id)

        if book is None:
            raise ValueError("A book in your cart no longer exists.")

        if item.quantity < 1:
            raise ValueError("Order quantities must be at least one.")

        if book.price < 0:
            raise ValueError("Book prices cannot be negative.")

        if not book.is_available:
            raise ValueError(
                f'"{book.title}" is currently unavailable.'
            )

        if item.quantity > book.stock_quantity:
            raise ValueError(
                f'Not enough stock available for "{book.title}".'
            )

        total_amount += book.price * item.quantity

        # Save the book details and price at the time of ordering.
        order_lines.append(
            {
                "book": book,
                "book_title": book.title,
                "unit_price": book.price,
                "quantity": item.quantity,
            }
        )

    # Preserve a snapshot of the shipping address.
    address_fields = [
        "full_name",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
        "phone_number",
    ]

    address_snapshot = {
        field: getattr(shipping_address, field)
        for field in address_fields
    }

    # Create the order in pending status.
    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        **address_snapshot,
    )

    # Create the individual order items.
    OrderItem.objects.bulk_create(
        [
            OrderItem(order=order, **line)
            for line in order_lines
        ]
    )

    # Create a pending payment record.
    payment = Payment.objects.create(
        order=order,
        method=payment_method,
        amount=total_amount,
    )

    # Initiate the mock payment.
    # This does not charge money or confirm successful payment.
    gateway_result = MockPaymentGateway.initiate_payment(payment)

    if gateway_result.get("success"):
        payment.transaction_reference = gateway_result["reference"]

        payment.save(
            update_fields=[
                "transaction_reference",
                "updated_at",
            ]
        )

    else:
        payment.status = Payment.Status.FAILED

        payment.failure_reason = gateway_result.get(
            "message",
            "Mock payment initiation failed.",
        )[:255]

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "updated_at",
            ]
        )

    return order, payment