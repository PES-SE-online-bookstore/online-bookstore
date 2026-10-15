from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Order


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

    return render(
        request,
        "orders/order_detail.html",
        {"order": order},
    )