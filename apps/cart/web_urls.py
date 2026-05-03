# === apps/cart/web_urls.py ===
from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('ajouter/<int:product_id>/', views.cart_add, name='add'),
    path('supprimer/<int:product_id>/', views.cart_remove, name='remove'),
    path('mettre-a-jour/<int:product_id>/', views.cart_update, name='update'),
    path('coupon/appliquer/', views.apply_coupon, name='apply_coupon'),
    path('coupon/retirer/', views.remove_coupon, name='remove_coupon'),
]
