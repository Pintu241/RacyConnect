from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'pickup', 'customer', 'collector', 'category', 'actual_weight', 'agreed_rate_per_kg', 'total_amount', 'payment_status', 'payment_method', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'category', 'created_at')
    search_fields = ('transaction_id', 'pickup__reference_id', 'customer__username', 'collector__username')
    readonly_fields = ('transaction_id', 'created_at')
