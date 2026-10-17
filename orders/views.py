from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Order, ReturnRequest


def _policy_deadline(start_time, policy_days):
    """Calculate the deadline for a cancellation or return request."""
    if start_time is None:
        return None

    return start_time + timedelta(days=policy_days)


def _policy_is_open(start_time, policy_days):
    """Return whether a policy window is still open."""
    deadline = _policy_deadline(start_time, policy_days)

    return deadline is not None and timezone.now() <= deadline


def _get_policy_days(setting_name):
    """Read a configurable policy window, defaulting to seven days."""
    try:
        days = int(getattr(settings, setting_name, 7))
    except (TypeError, ValueError):
        days = 7

    return max(days, 0)


@login_required
def order_history(request):
    """Display the logged-in user's order history."""
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items", "payments")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/order_history.html",
        {"orders": orders},
    )


@login_required
def order_detail(request, order_id):
    """Display details of an order belonging to the logged-in user."""
    order = get_object_or_404(
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__book", "payments"),
        pk=order_id,
    )

    cancellation_days = _get_policy_days(
        "ORDER_CANCELLATION_WINDOW_DAYS"
    )
    return_days = _get_policy_days("ORDER_RETURN_WINDOW_DAYS")

    cancellation_deadline = _policy_deadline(
        order.created_at,
        cancellation_days,
    )

    return_deadline = _policy_deadline(
        order.delivered_at,
        return_days,
    )

    cancellable_statuses = {
        Order.Status.PENDING,
        Order.Status.CONFIRMED,
        Order.Status.PROCESSING,
    }

    can_cancel = (
        order.status in cancellable_statuses
        and _policy_is_open(order.created_at, cancellation_days)
    )

    can_request_return = (
        order.status == Order.Status.DELIVERED
        and _policy_is_open(order.delivered_at, return_days)
    )

    existing_return_request = (
        ReturnRequest.objects.filter(order=order).first()
    )

    if existing_return_request is not None:
        can_request_return = False

    context = {
        "order": order,
        "can_cancel": can_cancel,
        "can_request_return": can_request_return,
        "cancellation_deadline": cancellation_deadline,
        "return_deadline": return_deadline,
        "cancellation_policy_days": cancellation_days,
        "return_policy_days": return_days,
        "return_request": existing_return_request,
    }

    return render(
        request,
        "orders/order_detail.html",
        context,
    )


@login_required
@require_POST
def cancel_order(request, order_id):
    """Cancel an eligible order within the configured policy window."""
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=order_id,
            user=request.user,
        )

        cancellation_days = _get_policy_days(
            "ORDER_CANCELLATION_WINDOW_DAYS"
        )

        cancellable_statuses = {
            Order.Status.PENDING,
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
        }

        if order.status not in cancellable_statuses:
            messages.error(
                request,
                "This order can no longer be cancelled.",
            )
            return redirect("orders:detail", order_id=order.pk)

        if not _policy_is_open(order.created_at, cancellation_days):
            messages.error(
                request,
                "The cancellation policy window has expired.",
            )
            return redirect("orders:detail", order_id=order.pk)

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])

    messages.success(request, "Your order has been cancelled.")

    return redirect("orders:detail", order_id=order.pk)


@login_required
@require_POST
def request_return(request, order_id):
    """Submit a return request for a delivered order within policy."""
    reason = request.POST.get("reason", "").strip()

    if not reason:
        messages.error(
            request,
            "Please provide a reason for your return request.",
        )
        return redirect("orders:detail", order_id=order_id)

    if len(reason) > 2000:
        messages.error(
            request,
            "Your return reason must not exceed 2000 characters.",
        )
        return redirect("orders:detail", order_id=order_id)

    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=order_id,
            user=request.user,
        )

        return_days = _get_policy_days("ORDER_RETURN_WINDOW_DAYS")

        if order.status != Order.Status.DELIVERED:
            messages.error(
                request,
                "A return can only be requested for a delivered order.",
            )
            return redirect("orders:detail", order_id=order.pk)

        if not _policy_is_open(order.delivered_at, return_days):
            messages.error(
                request,
                "The return policy window has expired or the delivery date is unavailable.",
            )
            return redirect("orders:detail", order_id=order.pk)

        if ReturnRequest.objects.filter(order=order).exists():
            messages.error(
                request,
                "A return request already exists for this order.",
            )
            return redirect("orders:detail", order_id=order.pk)

        ReturnRequest.objects.create(
            order=order,
            buyer=request.user,
            reason=reason,
        )

    messages.success(
        request,
        "Your return request has been submitted for review.",
    )

    return redirect("orders:detail", order_id=order.pk)