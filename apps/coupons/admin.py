from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'current_uses', 'max_uses', 'is_active', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'first_purchase_only')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
