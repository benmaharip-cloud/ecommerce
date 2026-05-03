from django.contrib import admin
from .models import DeliveryZone, Delivery


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price', 'estimated_days', 'is_active')
    list_editable = ('is_active', 'price')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'order', 'status', 'driver_name', 'estimated_arrival')
    list_filter = ('status',)
    search_fields = ('tracking_code', 'order__reference', 'driver_name')
