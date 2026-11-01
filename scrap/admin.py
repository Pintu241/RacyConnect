from django.contrib import admin
from .models import ScrapCategory

@admin.register(ScrapCategory)
class ScrapCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_rate_per_kg', 'min_rate_per_kg', 'max_rate_per_kg', 'unit', 'is_active', 'order')
    list_editable = ('base_rate_per_kg', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
