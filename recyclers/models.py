from django.db import models
from django.conf import settings
from scrap.models import ScrapCategory
import uuid

class PurchaseRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Under Review'),
        (STATUS_APPROVED, 'Approved / Logistics Scheduled'),
        (STATUS_FULFILLED, 'Fulfilled & Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    request_id = models.CharField(max_length=30, unique=True, editable=False)
    recycler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchase_requests'
    )
    category = models.ForeignKey(
        ScrapCategory,
        on_delete=models.PROTECT,
        related_name='purchase_requests'
    )
    requested_quantity_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Required bulk quantity in kilograms"
    )
    offered_price_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Offered procurement price per kg (₹)"
    )
    total_estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total procurement value: requested_quantity_kg * offered_price_per_kg"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    delivery_facility_address = models.TextField(help_text="Recycling plant or warehouse address")
    special_specifications = models.TextField(
        blank=True,
        help_text="Moisture tolerance, baling requirements, sorting criteria"
    )
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_id:
            short_code = uuid.uuid4().hex[:6].upper()
            self.request_id = f"PUR-{short_code}"
        self.total_estimated_cost = round(self.requested_quantity_kg * self.offered_price_per_kg, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.requested_quantity_kg}kg of {self.category.name} ({self.get_status_display()})"
