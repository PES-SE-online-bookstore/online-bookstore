from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile
from books.models import Book
from orders.models import Payment
from orders.services import create_order_from_cart

from .forms import CheckoutForm, ShippingAddressForm
from .models import Cart, CartItem, ShippingAddress


def is_buyer(user):
    if not user.is_authenticated:
        return False

    try:
        return user.profile.role == Profile.Role.BUYER
    except Profile.DoesNotExist:
        return False


@login_required
def cart_detail(request):
    if not is_buyer(request.user):
        messages.error(request, "Only buyers can access the shopping cart.")
        return redirect("book_catalogue")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("book").all()

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart,
            "items": items,
        },
    )


@login_required
@require_POST
def add_to_cart(request, book_id):
    if not is_buyer(request.user):
        messages.error(request, "Only buyers can add books to a cart.")
        return redirect("book_catalogue")

    quantity_value = request.POST.get("quantity", "1")

    try:
        quantity = int(quantity_value)
        if quantity < 1:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("book_detail", book_id=book_id)

    with transaction.atomic():
        book = get_object_or_404(
            Book.objects.select_for_update(),
            id=book_id,
            is_available=True,
        )

        if book.stock_quantity < quantity:
            messages.error(
                request,
                "The requested quantity exceeds the available stock.",
            )
            return redirect("book_detail", book_id=book.id)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item = CartItem.objects.filter(cart=cart, book=book).first()
        new_quantity = quantity + item.quantity if item else quantity

        if new_quantity > book.stock_quantity:
            messages.error(
                request,
                "The requested quantity exceeds the available stock.",
            )
            return redirect("book_detail", book_id=book.id)

        if item:
            item.quantity = new_quantity
            item.save(update_fields=["quantity", "updated_at"])
        else:
            CartItem.objects.create(
                cart=cart,
                book=book,
                quantity=quantity,
            )

    messages.success(request, f'"{book.title}" was added to your cart.')
    return redirect("cart:cart_detail")


@login_required
@require_POST
def update_cart_item(request, item_id):
    if not is_buyer(request.user):
        messages.error(request, "Only buyers can update a shopping cart.")
        return redirect("book_catalogue")

    quantity_value = request.POST.get("quantity", "")

    try:
        quantity = int(quantity_value)
        if quantity < 1:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart:cart_detail")

    with transaction.atomic():
        item = get_object_or_404(
            CartItem.objects.select_related("book").select_for_update(),
            id=item_id,
            cart__user=request.user,
        )

        book = Book.objects.select_for_update().get(id=item.book_id)

        if not book.is_available:
            messages.error(request, "This book is no longer available.")
            return redirect("cart:cart_detail")

        if quantity > book.stock_quantity:
            messages.error(
                request,
                "The requested quantity exceeds the available stock.",
            )
            return redirect("cart:cart_detail")

        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])

    messages.success(request, "Cart quantity updated.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    if not is_buyer(request.user):
        messages.error(request, "Only buyers can remove items from a cart.")
        return redirect("book_catalogue")

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    title = item.book.title
    item.delete()

    messages.success(request, f'"{title}" was removed from your cart.')
    return redirect("cart:cart_detail")


@login_required
def checkout(request):
    if not is_buyer(request.user):
        messages.error(request, "Only buyers can proceed to checkout.")
        return redirect("book_catalogue")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("book").all()

    if not items.exists():
        messages.error(
            request,
            "Your cart is empty. Add books before proceeding to checkout.",
        )
        return redirect("cart:cart_detail")

    addresses = ShippingAddress.objects.filter(user=request.user)

    selected_address = None
    address_id = (
        request.POST.get("address_id")
        if request.method == "POST"
        else None
    )

    if address_id:
        selected_address = addresses.filter(id=address_id).first()

    if request.method == "POST":
        checkout_form = CheckoutForm(request.POST)
        use_new_address = request.POST.get("use_new_address") == "yes"

        if use_new_address:
            address_form = ShippingAddressForm(request.POST)
            address_valid = address_form.is_valid()

            if checkout_form.is_valid() and address_valid:
                try:
                    with transaction.atomic():
                        address = address_form.save(commit=False)
                        address.user = request.user

                        if address.is_default:
                            ShippingAddress.objects.filter(
                                user=request.user,
                                is_default=True,
                            ).update(is_default=False)

                        address.save()

                        order, payment = create_order_from_cart(
                            user=request.user,
                            cart=cart,
                            shipping_address=address,
                            payment_method=checkout_form.cleaned_data[
                                "payment_method"
                            ],
                        )

                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.warning(
                        request,
                        (
                            f"Order #{order.pk} has been created with "
                            f"pending payment of {payment.amount}. "
                            "This is a test-mode workflow: no money was "
                            "charged, and payment has not been verified. "
                            "Your cart has been preserved."
                        ),
                    )

                    return render(
                        request,
                        "cart/checkout.html",
                        {
                            "cart": cart,
                            "items": cart.items.select_related("book").all(),
                            "addresses": ShippingAddress.objects.filter(
                                user=request.user
                            ),
                            "selected_address": address,
                            "address_form": ShippingAddressForm(),
                            "checkout_form": CheckoutForm(),
                            "checkout_pending": True,
                            "order": order,
                            "payment": payment,
                        },
                    )

        else:
            address_form = ShippingAddressForm()

            if checkout_form.is_valid() and selected_address is not None:
                try:
                    order, payment = create_order_from_cart(
                        user=request.user,
                        cart=cart,
                        shipping_address=selected_address,
                        payment_method=checkout_form.cleaned_data[
                            "payment_method"
                        ],
                    )

                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.warning(
                        request,
                        (
                            f"Order #{order.pk} has been created with "
                            f"pending payment of {payment.amount}. "
                            "This is a test-mode workflow: no money was "
                            "charged, and payment has not been verified. "
                            "Your cart has been preserved."
                        ),
                    )

                    return render(
                        request,
                        "cart/checkout.html",
                        {
                            "cart": cart,
                            "items": cart.items.select_related("book").all(),
                            "addresses": addresses,
                            "selected_address": selected_address,
                            "address_form": address_form,
                            "checkout_form": CheckoutForm(),
                            "checkout_pending": True,
                            "order": order,
                            "payment": payment,
                        },
                    )

            elif not selected_address:
                checkout_form.add_error(
                    None,
                    (
                        "Please select one of your saved shipping addresses "
                        "or enter a new address."
                    ),
                )

    else:
        checkout_form = CheckoutForm()
        address_form = ShippingAddressForm()
        selected_address = addresses.filter(is_default=True).first()

    return render(
        request,
        "cart/checkout.html",
        {
            "cart": cart,
            "items": items,
            "addresses": addresses,
            "selected_address": selected_address,
            "address_form": address_form,
            "checkout_form": checkout_form,
            "checkout_pending": False,
        },
    )