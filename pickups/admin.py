from django.contrib import admin
from .models import PickupRequest

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'customer', 'assigned_collector', 'category', 'estimated_weight', 'actual_weight', 'status', 'preferred_date', 'created_at')
    list_filter = ('status', 'category', 'preferred_date')
    search_fields = ('reference_id', 'customer__username', 'customer__first_name', 'assigned_collector__username', 'pickup_address', 'postal_code')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
