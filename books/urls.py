from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.book_catalogue, name="book_catalogue"),
    path(
        "<int:book_id>/",
        views.book_detail,
        name="book_detail",
    ),
    path(
        "seller/create/",
        views.create_listing,
        name="create_listing",
    ),
]