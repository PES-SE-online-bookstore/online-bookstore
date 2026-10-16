import logging

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


ORDER_STATUS_MESSAGES = {
    "CONFIRMED": {
        "subject": "Your Online Bookstore order is confirmed",
        "message": (
            "Your order has been confirmed. "
            "We will keep you updated about its progress."
        ),
    },
    "SHIPPED": {
        "subject": "Your Online Bookstore order has been shipped",
        "message": (
            "Your order has been shipped. "
            "Thank you for shopping with us."
        ),
    },
    "DELIVERED": {
        "subject": "Your Online Bookstore order has been delivered",
        "message": (
            "Your order has been marked as delivered. "
            "We hope you enjoy your purchase."
        ),
    },
}


def send_order_status_notification(order):
    """
    Send an email notification for a supported order status.

    Notifications are sent only for CONFIRMED, SHIPPED, and DELIVERED
    statuses. Email failures are logged and do not propagate to callers.
    """
    status = order.status
    notification = ORDER_STATUS_MESSAGES.get(status)

    if notification is None:
        return False

    recipient = (order.user.email or "").strip()

    if not recipient:
        logger.warning(
            "Cannot send order-status notification for order %s: "
            "the buyer has no email address.",
            order.pk,
        )
        return False

    book_lines = []

    for item in order.items.all():
        book_lines.append(
            f"- {item.book_title} "
            f"(Quantity: {item.quantity}, "
            f"Unit price: {item.unit_price})"
        )

    items_text = "\n".join(book_lines) or "No item details available."

    message = (
        f"Hello {order.full_name},\n\n"
        f"{notification['message']}\n\n"
        f"Order number: #{order.pk}\n"
        f"Order status: {order.get_status_display()}\n"
        f"Order total: {order.total_amount}\n\n"
        f"Items:\n{items_text}\n\n"
        "Shipping address:\n"
        f"{order.address_line_1}\n"
        f"{order.address_line_2}\n"
        f"{order.city}, {order.state} {order.postal_code}\n"
        f"{order.country}\n\n"
        "Thank you for shopping with Online Bookstore."
    )

    try:
        sent_count = send_mail(
            subject=notification["subject"],
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send status notification for order %s.",
            order.pk,
        )
        return False

    return sent_count == 1