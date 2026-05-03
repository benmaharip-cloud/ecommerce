from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"
urlpatterns = [
    path("connexion/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("inscription/", views.register, name="register"),
    path("profil/", views.profile, name="profile"),
    path("mes-coupons/", views.my_coupons, name="my_coupons"),
    path("mot-de-passe-oublie/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset.html",
        email_template_name="users/password_reset_email.txt",
        success_url="/compte/mot-de-passe-envoye/"
    ), name="password_reset"),
    path("mot-de-passe-envoye/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"
    ), name="password_reset_done"),
    path("reinitialiser/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html",
        success_url="/compte/mot-de-passe-reinitialise/"
    ), name="password_reset_confirm"),
    path("mot-de-passe-reinitialise/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),
]
