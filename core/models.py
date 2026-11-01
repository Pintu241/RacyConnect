from django.db import models
from django.conf import settings
from pickups.models import PickupRequest

class Complaint(models.Model):
    STATUS_OPEN = 'OPEN'
    STATUS_INVESTIGATING = 'IN_INVESTIGATION'
    STATUS_RESOLVED = 'RESOLVED'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_INVESTIGATING, 'Under Investigation'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    pickup = models.ForeignKey(
        PickupRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints',
        help_text="Optional related pickup request"
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    resolution_notes = models.TextField(blank=True, help_text="Notes added by administrator upon resolution")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint #{self.id}: {self.subject} ({self.get_status_display()})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
