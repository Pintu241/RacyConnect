from django.contrib import admin
from .models import PurchaseRequest

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'recycler', 'category', 'requested_quantity_kg', 'offered_price_per_kg', 'total_estimated_cost', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('request_id', 'recycler__username', 'recycler__first_name', 'delivery_facility_address')
    readonly_fields = ('request_id', 'total_estimated_cost', 'created_at', 'updated_at')
