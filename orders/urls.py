from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_history, name="history"),
    path("<int:order_id>/", views.order_detail, name="detail"),
]