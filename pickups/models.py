from django.db import models
from django.conf import settings
from scrap.models import ScrapCategory
import uuid

class PickupRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Collector Assignment'),
        (STATUS_ACCEPTED, 'Collector Assigned / Scheduled'),
        (STATUS_IN_PROGRESS, 'Out for Pickup / In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00 - 12:00', 'Morning (9:00 AM - 12:00 PM)'),
        ('12:00 - 15:00', 'Afternoon (12:00 PM - 3:00 PM)'),
        ('15:00 - 18:00', 'Late Afternoon (3:00 PM - 6:00 PM)'),
        ('18:00 - 20:00', 'Evening (6:00 PM - 8:00 PM)'),
    ]

    reference_id = models.CharField(max_length=30, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pickup_requests'
    )
    assigned_collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups'
    )
    category = models.ForeignKey(
        ScrapCategory,
        on_delete=models.PROTECT,
        related_name='pickup_requests'
    )
    estimated_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Estimated scrap weight in kg"
    )
    actual_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual weight recorded by collector on site (kg)"
    )
    agreed_rate_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final agreed rate per kg upon inspection"
    )
    pickup_address = models.TextField(help_text="Detailed doorstep pickup address")
    city = models.CharField(max_length=100, default='Green City')
    postal_code = models.CharField(max_length=20)
    contact_phone = models.CharField(max_length=20, blank=True)
    preferred_date = models.DateField(help_text="Preferred date of scrap collection")
    preferred_time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES, default='09:00 - 12:00')
    scrap_image = models.ImageField(upload_to='scrap_photos/', blank=True, null=True, help_text="Photo of scrap items")
    notes = models.TextField(blank=True, help_text="Special instructions, floor number, landmark, etc.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_id:
            short_code = uuid.uuid4().hex[:6].upper()
            self.reference_id = f"RC-{short_code}"
        super().save(*args, **kwargs)

    @property
    def estimated_total_amount(self):
        if self.estimated_weight and self.category:
            return round(self.estimated_weight * self.category.base_rate_per_kg, 2)
        return 0.0

    @property
    def final_total_amount(self):
        if self.actual_weight and self.agreed_rate_per_kg:
            return round(self.actual_weight * self.agreed_rate_per_kg, 2)
        return None

    def can_be_cancelled(self, user):
        return (user == self.customer or user.is_platform_admin) and self.status in [self.STATUS_PENDING, self.STATUS_ACCEPTED]

    def can_be_accepted(self, user):
        return user.is_collector and self.status == self.STATUS_PENDING

    def can_be_completed(self, user):
        return (user == self.assigned_collector or user.is_platform_admin) and self.status in [self.STATUS_ACCEPTED, self.STATUS_IN_PROGRESS]

    def __str__(self):
        return f"{self.reference_id} - {self.category.name} ({self.customer.username}) - {self.get_status_display()}"
