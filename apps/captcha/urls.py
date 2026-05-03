from django.urls import path
from . import views

urlpatterns = [
    path("get/", views.get_captcha, name="captcha_get"),
    path("verify/", views.verify_captcha, name="captcha_verify"),
]
