from django.contrib import admin
from .models import Complaint, ContactMessage

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'pickup', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'description', 'user__username', 'resolution_notes')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
