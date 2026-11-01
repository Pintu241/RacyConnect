from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scrap.models import ScrapCategory
from pickups.models import PickupRequest
from transactions.models import Transaction
from recyclers.models import PurchaseRequest
from core.models import Complaint, ContactMessage
from accounts.models import CollectorProfile, RecyclerProfile
from decimal import Decimal
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial realistic data for RecyConnect demonstration'

    def handle(self, *args, **options):
        self.stdout.write("Seeding RecyConnect platform data...")

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@recyconnect.org',
                'first_name': 'Platform',
                'last_name': 'Admin',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'city': 'Green Metro',
                'phone_number': '+91 98765 00001',
            }
        )
        if created or not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))

        # 2. Create Scrap Categories
        categories_data = [
            {
                'name': 'Paper & Newspapers',
                'description': 'Old newspapers, magazines, office white paper, textbooks, shredded documents.',
                'icon': 'bi-newspaper',
                'base_rate_per_kg': Decimal('14.00'),
                'min_rate_per_kg': Decimal('12.00'),
                'max_rate_per_kg': Decimal('16.00'),
                'recyclability_impact': 'Recycling 1 ton of paper saves 17 trees and 7,000 gallons of water.',
                'order': 1
            },
            {
                'name': 'Cardboard & Cartons',
                'description': 'Brown corrugated cardboard boxes, packaging cartons, food delivery boxes.',
                'icon': 'bi-box-seam',
                'base_rate_per_kg': Decimal('11.00'),
                'min_rate_per_kg': Decimal('9.00'),
                'max_rate_per_kg': Decimal('13.00'),
                'recyclability_impact': 'Recycled cardboard uses 24% less energy than making virgin cardboard.',
                'order': 2
            },
            {
                'name': 'Plastics & PET Bottles',
                'description': 'Water/soda bottles (PET), shampoo bottles (HDPE), milk packets, hard plastic buckets.',
                'icon': 'bi-cup-straw',
                'base_rate_per_kg': Decimal('18.00'),
                'min_rate_per_kg': Decimal('15.00'),
                'max_rate_per_kg': Decimal('22.00'),
                'recyclability_impact': 'Diverts microplastics from waterways and saves crude petroleum extraction.',
                'order': 3
            },
            {
                'name': 'Metals & Iron Scrap',
                'description': 'Iron bars, tins, steel utensils, aluminum beverage cans, brass, copper wires.',
                'icon': 'bi-tools',
                'base_rate_per_kg': Decimal('36.00'),
                'min_rate_per_kg': Decimal('28.00'),
                'max_rate_per_kg': Decimal('48.00'),
                'recyclability_impact': 'Recycling metal saves up to 95% of energy compared to ore mining.',
                'order': 4
            },
            {
                'name': 'E-Waste & Electronics',
                'description': 'Old computers, broken laptops, smartphones, PCBs, motherboards, electrical cords, chargers.',
                'icon': 'bi-cpu',
                'base_rate_per_kg': Decimal('45.00'),
                'min_rate_per_kg': Decimal('35.00'),
                'max_rate_per_kg': Decimal('85.00'),
                'recyclability_impact': 'Recovers critical rare earth metals and prevents hazardous lead/mercury leaching.',
                'order': 5
            },
            {
                'name': 'Glass Bottles & Jars',
                'description': 'Beverage glass bottles, beer bottles, clear pickle jars, sauce bottles.',
                'icon': 'bi-droplet',
                'base_rate_per_kg': Decimal('4.50'),
                'min_rate_per_kg': Decimal('3.00'),
                'max_rate_per_kg': Decimal('6.00'),
                'recyclability_impact': 'Glass is 100% recyclable infinitely with zero loss in purity or quality.',
                'order': 6
            },
            {
                'name': 'Lead-Acid Batteries',
                'description': 'Automobile car batteries, inverter lead-acid batteries, solar backup cells.',
                'icon': 'bi-battery-charging',
                'base_rate_per_kg': Decimal('82.00'),
                'min_rate_per_kg': Decimal('75.00'),
                'max_rate_per_kg': Decimal('95.00'),
                'recyclability_impact': 'Over 98% of lead and plastic in used batteries can be safely reclaimed.',
                'order': 7
            },
        ]

        categories_map = {}
        for cat in categories_data:
            obj, _ = ScrapCategory.objects.get_or_create(
                name=cat['name'],
                defaults=cat
            )
            categories_map[cat['name']] = obj

        self.stdout.write(self.style.SUCCESS(f'Created {len(categories_map)} scrap categories'))

        # 3. Create Sample Customers
        customer1, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'rahul.sharma@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'role': User.ROLE_CUSTOMER,
                'phone_number': '+91 98234 11223',
                'address': 'Flat 402, Green View Residency, Park Road',
                'city': 'Green City',
                'state': 'State',
                'postal_code': '110025',
            }
        )
        customer1.set_password('pass123')
        customer1.save()

        customer2, _ = User.objects.get_or_create(
            username='business1',
            defaults={
                'email': 'procure@nexustechnologies.com',
                'first_name': 'Nexus',
                'last_name': 'Tech Hub',
                'role': User.ROLE_CUSTOMER,
                'phone_number': '+91 98450 99887',
                'address': 'Tower B, 3rd Floor, Cyber City Tech Park',
                'city': 'Green City',
                'state': 'State',
                'postal_code': '110034',
            }
        )
        customer2.set_password('pass123')
        customer2.save()

        # 4. Create Sample Collectors
        collector1, _ = User.objects.get_or_create(
            username='collector1',
            defaults={
                'email': 'mohan.lal@collector.recyconnect.org',
                'first_name': 'Mohan',
                'last_name': 'Lal',
                'role': User.ROLE_COLLECTOR,
                'phone_number': '+91 91234 56789',
                'address': 'Ward 12, Old Market Bazaar',
                'city': 'Green City',
                'state': 'State',
                'postal_code': '110025',
            }
        )
        collector1.set_password('pass123')
        collector1.save()
        cprofile1, _ = CollectorProfile.objects.get_or_create(user=collector1)
        cprofile1.service_area = 'Green City East, Park Road, Metro Sector 1-5'
        cprofile1.vehicle_type = 'e_rickshaw'
        cprofile1.is_verified = True
        cprofile1.id_proof_type = 'Aadhaar Card'
        cprofile1.id_proof_number = 'XXXX-XXXX-8921'
        cprofile1.rating = Decimal('4.90')
        cprofile1.total_collected_weight = Decimal('1450.50')
        cprofile1.total_earnings = Decimal('38200.00')
        cprofile1.save()

        collector2, _ = User.objects.get_or_create(
            username='collector2',
            defaults={
                'email': 'ramesh.kumar@collector.recyconnect.org',
                'first_name': 'Ramesh',
                'last_name': 'Kumar',
                'role': User.ROLE_COLLECTOR,
                'phone_number': '+91 98711 22334',
                'address': 'Plot 45, Industrial Belt Phase 1',
                'city': 'Green City',
                'state': 'State',
                'postal_code': '110034',
            }
        )
        collector2.set_password('pass123')
        collector2.save()
        cprofile2, _ = CollectorProfile.objects.get_or_create(user=collector2)
        cprofile2.service_area = 'Cyber City Tech Park & Sector 7-10'
        cprofile2.vehicle_type = 'cycle_cart'
        cprofile2.is_verified = False  # Pending verification for testing admin verification!
        cprofile2.id_proof_type = 'Voter ID'
        cprofile2.id_proof_number = 'VTR-8812903'
        cprofile2.rating = Decimal('4.70')
        cprofile2.save()

        # 5. Create Sample Recycler
        recycler1, _ = User.objects.get_or_create(
            username='recycler1',
            defaults={
                'email': 'contact@ecogreenrecyclers.com',
                'first_name': 'EcoGreen',
                'last_name': 'Recycling Solutions',
                'role': User.ROLE_RECYCLER,
                'phone_number': '+91 11 4455 6677',
                'address': 'Plant 18, Eco Industrial Park, Highway 48',
                'city': 'Green City',
                'state': 'State',
                'postal_code': '110098',
            }
        )
        recycler1.set_password('pass123')
        recycler1.save()
        rprofile1, _ = RecyclerProfile.objects.get_or_create(user=recycler1)
        rprofile1.company_name = 'EcoGreen Reclaim & Smelting Ltd.'
        rprofile1.license_number = 'PCB-2024-REC-90812'
        rprofile1.gst_number = '07AAACE9876Q1Z8'
        rprofile1.facility_address = 'Plant 18, Eco Industrial Park, Highway 48'
        rprofile1.processing_capacity_tons = Decimal('250.00')
        rprofile1.materials_accepted = 'Cardboard, PET Bottles, Iron & Metals, Electronic Scrap'
        rprofile1.is_verified = True
        rprofile1.save()

        self.stdout.write(self.style.SUCCESS('Users created: customer1, business1, collector1, collector2, recycler1 (password: pass123)'))

        # 6. Create Sample Pickup Requests across different statuses
        today = date.today()

        # Completed Pickup with Transaction
        p_completed, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-COMP1',
            defaults={
                'customer': customer1,
                'assigned_collector': collector1,
                'category': categories_map['Paper & Newspapers'],
                'estimated_weight': Decimal('25.00'),
                'actual_weight': Decimal('28.50'),
                'agreed_rate_per_kg': Decimal('14.00'),
                'pickup_address': 'Flat 402, Green View Residency, Park Road',
                'city': 'Green City',
                'postal_code': '110025',
                'contact_phone': '+91 98234 11223',
                'preferred_date': today - timedelta(days=2),
                'preferred_time_slot': '09:00 - 12:00',
                'status': PickupRequest.STATUS_COMPLETED,
                'notes': '4 big bundles of daily newspapers and magazines',
            }
        )
        if not hasattr(p_completed, 'transaction'):
            Transaction.objects.get_or_create(
                pickup=p_completed,
                defaults={
                    'customer': customer1,
                    'collector': collector1,
                    'category': p_completed.category,
                    'actual_weight': p_completed.actual_weight,
                    'agreed_rate_per_kg': p_completed.agreed_rate_per_kg,
                    'total_amount': Decimal('399.00'),
                    'payment_method': 'cash',
                    'payment_status': Transaction.STATUS_PAID,
                    'notes': 'Doorstep weighed using calibrated digital scale. Paid in cash.',
                }
            )

        # Another Completed Pickup (Metals)
        p_completed2, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-COMP2',
            defaults={
                'customer': customer2,
                'assigned_collector': collector1,
                'category': categories_map['Metals & Iron Scrap'],
                'estimated_weight': Decimal('60.00'),
                'actual_weight': Decimal('64.00'),
                'agreed_rate_per_kg': Decimal('38.00'),
                'pickup_address': 'Tower B, 3rd Floor, Cyber City Tech Park',
                'city': 'Green City',
                'postal_code': '110034',
                'contact_phone': '+91 98450 99887',
                'preferred_date': today - timedelta(days=5),
                'preferred_time_slot': '12:00 - 15:00',
                'status': PickupRequest.STATUS_COMPLETED,
                'notes': 'Dismantled server racks and iron brackets.',
            }
        )
        if not hasattr(p_completed2, 'transaction'):
            Transaction.objects.get_or_create(
                pickup=p_completed2,
                defaults={
                    'customer': customer2,
                    'collector': collector1,
                    'category': p_completed2.category,
                    'actual_weight': p_completed2.actual_weight,
                    'agreed_rate_per_kg': p_completed2.agreed_rate_per_kg,
                    'total_amount': Decimal('2432.00'),
                    'payment_method': 'upi',
                    'payment_status': Transaction.STATUS_PAID,
                    'notes': 'Instant UPI settlement done to business account.',
                }
            )

        # In Progress Pickup
        p_inprogress, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-INPRG',
            defaults={
                'customer': customer1,
                'assigned_collector': collector1,
                'category': categories_map['Cardboard & Cartons'],
                'estimated_weight': Decimal('35.00'),
                'pickup_address': 'Flat 402, Green View Residency, Park Road',
                'city': 'Green City',
                'postal_code': '110025',
                'contact_phone': '+91 98234 11223',
                'preferred_date': today,
                'preferred_time_slot': '12:00 - 15:00',
                'status': PickupRequest.STATUS_IN_PROGRESS,
                'notes': 'Flat-packed appliance delivery boxes.',
            }
        )

        # Accepted / Scheduled Pickup
        p_accepted, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-SCHED',
            defaults={
                'customer': customer2,
                'assigned_collector': collector1,
                'category': categories_map['E-Waste & Electronics'],
                'estimated_weight': Decimal('40.00'),
                'pickup_address': 'Tower B, 3rd Floor, Cyber City Tech Park',
                'city': 'Green City',
                'postal_code': '110034',
                'contact_phone': '+91 98450 99887',
                'preferred_date': today + timedelta(days=1),
                'preferred_time_slot': '15:00 - 18:00',
                'status': PickupRequest.STATUS_ACCEPTED,
                'notes': 'Old office desktop CPUs and keyboards.',
            }
        )

        # Open / Pending Pickup (Waiting for collector to accept)
        p_pending1, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-OPEN1',
            defaults={
                'customer': customer1,
                'category': categories_map['Plastics & PET Bottles'],
                'estimated_weight': Decimal('15.00'),
                'pickup_address': 'Flat 402, Green View Residency, Park Road',
                'city': 'Green City',
                'postal_code': '110025',
                'contact_phone': '+91 98234 11223',
                'preferred_date': today + timedelta(days=2),
                'preferred_time_slot': '09:00 - 12:00',
                'status': PickupRequest.STATUS_PENDING,
                'notes': 'Clean plastic bottles and containers segregated.',
            }
        )

        p_pending2, _ = PickupRequest.objects.get_or_create(
            reference_id='RC-2026-OPEN2',
            defaults={
                'customer': customer2,
                'category': categories_map['Lead-Acid Batteries'],
                'estimated_weight': Decimal('75.00'),
                'pickup_address': 'Tower B Basement, Cyber City Tech Park',
                'city': 'Green City',
                'postal_code': '110034',
                'contact_phone': '+91 98450 99887',
                'preferred_date': today + timedelta(days=3),
                'preferred_time_slot': '12:00 - 15:00',
                'status': PickupRequest.STATUS_PENDING,
                'notes': '2 heavy UPS inverter batteries replaced during overhaul.',
            }
        )

        # 7. Create Sample Purchase Requests from Recycler
        PurchaseRequest.objects.get_or_create(
            request_id='PUR-9901',
            defaults={
                'recycler': recycler1,
                'category': categories_map['Cardboard & Cartons'],
                'requested_quantity_kg': Decimal('2500.00'),
                'offered_price_per_kg': Decimal('12.50'),
                'total_estimated_cost': Decimal('31250.00'),
                'status': PurchaseRequest.STATUS_APPROVED,
                'delivery_facility_address': 'Plant 18, Eco Industrial Park, Highway 48',
                'special_specifications': 'Moisture below 12%, baled or bundled securely.',
                'admin_notes': 'Assigned to Green City East aggregate depot.',
            }
        )

        PurchaseRequest.objects.get_or_create(
            request_id='PUR-9902',
            defaults={
                'recycler': recycler1,
                'category': categories_map['Metals & Iron Scrap'],
                'requested_quantity_kg': Decimal('1200.00'),
                'offered_price_per_kg': Decimal('40.00'),
                'total_estimated_cost': Decimal('48000.00'),
                'status': PurchaseRequest.STATUS_PENDING,
                'delivery_facility_address': 'Plant 18, Eco Industrial Park, Highway 48',
                'special_specifications': 'Heavy melting scrap preferred.',
            }
        )

        # 8. Create Sample Complaint
        Complaint.objects.get_or_create(
            subject='Delay in morning collection time slot',
            defaults={
                'user': customer1,
                'pickup': p_completed,
                'description': 'The collector arrived 45 minutes late due to traffic, but was courteous and weighed everything accurately.',
                'status': Complaint.STATUS_RESOLVED,
                'resolution_notes': 'Contacted collector Mohan Lal; collector updated regarding traffic advisories.',
            }
        )

        ContactMessage.objects.get_or_create(
            email='greenwarrior@society.org',
            defaults={
                'name': 'Pooja Verma',
                'phone': '+91 99887 76655',
                'subject': 'Inquiry about bulk collection for Residential Society',
                'message': 'We have 350 flats in our gated society and would like to organize monthly community scrap collection drives with RecyConnect.',
            }
        )

        self.stdout.write(self.style.SUCCESS('RecyConnect seed data populated successfully!'))
