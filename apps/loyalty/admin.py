from django.contrib import admin
from .models import LoyaltyAccount, LoyaltyTransaction


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'total_points_earned', 'level')
    list_filter = ('level',)
    search_fields = ('user__email', 'user__first_name')


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'points', 'transaction_type', 'description', 'created_at')
    list_filter = ('transaction_type',)
