from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CollectorProfile, RecyclerProfile

class CollectorProfileInline(admin.StackedInline):
    model = CollectorProfile
    can_delete = False
    verbose_name_plural = 'Collector Profile Details'

class RecyclerProfileInline(admin.StackedInline):
    model = RecyclerProfile
    can_delete = False
    verbose_name_plural = 'Recycler Profile Details'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('RecyConnect Role & Contact', {
            'fields': ('role', 'phone_number', 'address', 'city', 'state', 'postal_code', 'profile_picture')
        }),
    )
    list_display = ('username', 'email', 'get_full_name', 'role', 'city', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'city')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

@admin.register(CollectorProfile)
class CollectorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_area', 'vehicle_type', 'is_verified', 'is_available', 'rating', 'total_collected_weight', 'total_earnings')
    list_filter = ('is_verified', 'is_available', 'vehicle_type')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'service_area', 'id_proof_number')
    actions = ['verify_collectors', 'unverify_collectors']

    def verify_collectors(self, request, queryset):
        queryset.update(is_verified=True)
    verify_collectors.short_description = "Mark selected collectors as Verified"

    def unverify_collectors(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_collectors.short_description = "Mark selected collectors as Unverified"

@admin.register(RecyclerProfile)
class RecyclerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'license_number', 'processing_capacity_tons', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('company_name', 'user__username', 'license_number', 'gst_number')
