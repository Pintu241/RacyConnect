from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_COLLECTOR = 'collector'
    ROLE_RECYCLER = 'recycler'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Household / Business Customer'),
        (ROLE_COLLECTOR, 'Scrap Collector'),
        (ROLE_RECYCLER, 'Recycling Company'),
        (ROLE_ADMIN, 'Platform Administrator'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        help_text="User role in the RecyConnect ecosystem"
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Green City')
    state = models.CharField(max_length=100, default='State')
    postal_code = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    @property
    def is_collector(self):
        return self.role == self.ROLE_COLLECTOR

    @property
    def is_recycler(self):
        return self.role == self.ROLE_RECYCLER

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def __str__(self):
        name = self.get_full_name() or self.username
        return f"{name} ({self.get_role_display()})"


class CollectorProfile(models.Model):
    VEHICLE_CHOICES = [
        ('cycle_cart', 'Bicycle Cart / Handcart'),
        ('e_rickshaw', 'Electric Loader / E-Rickshaw'),
        ('mini_truck', 'Mini Truck / Commercial Van'),
        ('two_wheeler', 'Two-Wheeler Cargo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='collector_profile')
    service_area = models.CharField(max_length=255, default='Downtown & Metro Area', help_text="Areas or neighborhoods served")
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES, default='e_rickshaw')
    is_verified = models.BooleanField(default=False, help_text="Verified by RecyConnect platform")
    id_proof_type = models.CharField(max_length=50, default='National ID / Aadhaar')
    id_proof_number = models.CharField(max_length=100, blank=True)
    id_proof_document = models.ImageField(upload_to='id_proofs/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_collected_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True, help_text="Available to accept new pickups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Collector: {self.user.get_full_name() or self.user.username} {'(Verified)' if self.is_verified else '(Pending Verification)'}"


class RecyclerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recycler_profile')
    company_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100, blank=True)
    gst_number = models.CharField(max_length=100, blank=True)
    facility_address = models.TextField(blank=True)
    processing_capacity_tons = models.DecimalField(max_digits=8, decimal_places=2, default=50.00, help_text="Monthly processing capacity in tons")
    materials_accepted = models.TextField(default="Paper, Plastic, Metal, E-Waste, Glass", help_text="Materials accepted for bulk processing")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.role == User.ROLE_COLLECTOR:
        CollectorProfile.objects.get_or_create(user=instance)
    elif instance.role == User.ROLE_RECYCLER:
        RecyclerProfile.objects.get_or_create(
            user=instance,
            defaults={'company_name': instance.get_full_name() or f"{instance.username} Recycling Corp"}
        )
