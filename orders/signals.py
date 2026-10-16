import logging

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from orders.email_notifications import send_order_status_notification
from orders.models import Order


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def capture_previous_order_status(sender, instance, **kwargs):
    """
    Capture the previous status and set the delivery timestamp on transition.
    """
    if not instance.pk:
        instance._previous_order_status = None

        # Handle orders created directly in DELIVERED status.
        if instance.status == Order.Status.DELIVERED and not instance.delivered_at:
            instance.delivered_at = timezone.now()

        return

    previous_order = (
        sender.objects.filter(pk=instance.pk)
        .values("status", "delivered_at")
        .first()
    )

    if previous_order is None:
        instance._previous_order_status = None
        return

    instance._previous_order_status = previous_order["status"]

    # Preserve an existing delivery timestamp.
    if instance.status == Order.Status.DELIVERED:
        if not previous_order["delivered_at"]:
            instance.delivered_at = timezone.now()
        else:
            instance.delivered_at = previous_order["delivered_at"]
    elif previous_order["status"] != Order.Status.DELIVERED:
        # An order that has not been delivered must not have a delivery time.
        instance.delivered_at = None


@receiver(post_save, sender=Order)
def notify_buyer_of_order_status_change(
    sender,
    instance,
    created,
    **kwargs,
):
    """
    Schedule an email when an existing order enters a supported status.
    """
    if created:
        return

    previous_status = getattr(
        instance,
        "_previous_order_status",
        None,
    )

    if previous_status == instance.status:
        return

    if instance.status not in {
        Order.Status.CONFIRMED,
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
    }:
        return

    order_id = instance.pk

    def send_notification():
        try:
            order = Order.objects.select_related("user").get(pk=order_id)
            send_order_status_notification(order)
        except Exception:
            logger.exception(
                "Could not process status notification for order %s.",
                order_id,
            )

    transaction.on_commit(send_notification)