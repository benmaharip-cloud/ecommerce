from django.urls import path
from . import views
urlpatterns = [
    path("checkout/<int:order_id>/", views.stripe_checkout_view, name="checkout"),
    path("webhook/", views.stripe_webhook, name="webhook"),
    path("succes/<int:order_id>/", views.stripe_success, name="success"),
]
