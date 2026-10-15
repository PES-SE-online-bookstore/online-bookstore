from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    # Book catalogue and details
    path("", views.book_catalogue, name="book_catalogue"),
    path("<int:book_id>/", views.book_detail, name="book_detail"),

    # Book reviews
    path(
        "<int:book_id>/review/",
        views.submit_review,
        name="submit_review",
    ),

    # Buyer wishlist
    path("wishlist/", views.wishlist, name="wishlist"),
    path(
        "wishlist/add/<int:book_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist",
    ),
    path(
        "wishlist/remove/<int:book_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),

    # Seller listing management
    path("seller/create/", views.create_listing, name="create_listing"),
    path("seller/listings/", views.my_listings, name="my_listings"),
    path(
        "seller/listings/<int:book_id>/edit/",
        views.edit_listing,
        name="edit_listing",
    ),
    path(
        "seller/listings/<int:book_id>/delete/",
        views.delete_listing,
        name="delete_listing",
    ),
]