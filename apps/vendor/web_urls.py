from django.urls import path
from . import views

app_name = "vendor"
urlpatterns = [
    path("", views.VendorDashboardView.as_view(), name="dashboard"),
    path("produits/", views.VendorProductListView.as_view(), name="products"),
    path("commandes/", views.VendorOrderListView.as_view(), name="orders"),
    path("taches/", views.VendorTasksView.as_view(), name="tasks"),
    path("taches/", views.VendorTasksView.as_view(), name="tasks"),
    path("stats/api/", views.VendorStatsApiView.as_view(), name="stats_api"),
]
