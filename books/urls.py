from django.urls import path

from . import views

urlpatterns = [
    path("", views.book_catalogue, name="book_catalogue"),
]