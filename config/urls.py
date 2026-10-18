"""
URL configuration for the online bookstore.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from config.health import health_check


urlpatterns = [
    # Send visitors directly to the book catalogue.
    path(
        "",
        RedirectView.as_view(
            pattern_name="books:book_catalogue",
            permanent=False,
        ),
        name="home",
    ),
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("books/", include("books.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
]