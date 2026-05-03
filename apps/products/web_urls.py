from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("produits/", views.ProductListView.as_view(), name="list"),
    path("produits/recherche/", views.ProductListView.as_view(), name="search"),
    path("recherche-image/", views.ImageSearchView.as_view(), name="image_search"),
    path("produits/<slug:slug>/", views.ProductDetailView.as_view(), name="detail"),
    path("produits/<slug:slug>/apercu/", views.product_preview, name="preview"),
]
