from django.db import models
from django.conf import settings
from pickups.models import PickupRequest
from scrap.models import ScrapCategory
import uuid

class Transaction(models.Model):
    STATUS_PAID = 'PAID'
    STATUS_PENDING = 'PENDING'
    STATUS_FAILED = 'FAILED'

    PAYMENT_STATUS_CHOICES = [
        (STATUS_PAID, 'Paid to Customer'),
        (STATUS_PENDING, 'Payment Pending'),
        (STATUS_FAILED, 'Payment Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Hand (Doorstep)'),
        ('upi', 'UPI / QR Scan (Instant Transfer)'),
        ('bank_transfer', 'Direct Bank Transfer / NEFT'),
        ('wallet', 'RecyConnect Green Wallet'),
    ]

    transaction_id = models.CharField(max_length=40, unique=True, editable=False)
    pickup = models.OneToOneField(
        PickupRequest,
        on_delete=models.CASCADE,
        related_name='transaction'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_transactions'
    )
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collector_transactions'
    )
    category = models.ForeignKey(
        ScrapCategory,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    actual_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Verified scrap weight in kilograms"
    )
    agreed_rate_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Agreed price per kilogram in local currency (₹)"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated total: actual_weight * agreed_rate_per_kg"
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=STATUS_PAID
    )
    notes = models.TextField(blank=True, help_text="Transaction remarks or digital receipt reference")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            short_code = uuid.uuid4().hex[:8].upper()
            self.transaction_id = f"TXN-{short_code}"
        
        # Enforce server-side calculation of total amount:
        # total_amount = actual_weight_kg * agreed_rate_per_kg
        self.total_amount = round(self.actual_weight * self.agreed_rate_per_kg, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - ₹{self.total_amount} ({self.customer.username} via {self.collector.username})"
