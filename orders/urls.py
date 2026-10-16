from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_history, name="history"),
    path("<int:order_id>/", views.order_detail, name="detail"),
    path(
        "<int:order_id>/cancel/",
        views.cancel_order,
        name="cancel",
    ),
    path(
        "<int:order_id>/return/",
        views.request_return,
        name="request_return",
    ),
]