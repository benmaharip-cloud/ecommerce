from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('passer/', views.checkout, name='checkout'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('suivi/', views.order_tracking, name='tracking'),
    path('<int:pk>/confirmation/', views.order_confirmation, name='confirmation'),
]
