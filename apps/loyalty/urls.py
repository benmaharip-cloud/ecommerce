from django.urls import path
from . import views

app_name = "loyalty"
urlpatterns = [
    path("", views.loyalty_account, name="account"),
    path("echanger/", views.redeem_points, name="redeem"),
]
