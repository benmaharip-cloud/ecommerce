from django.urls import path
app_name = 'coupons'
urlpatterns = []

from . import views as coupon_views
urlpatterns += [path('validate/', coupon_views.validate_coupon, name='validate')]
