from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from scrap.models import ScrapCategory
from pickups.models import PickupRequest
from transactions.models import Transaction
from recyclers.models import PurchaseRequest
from accounts.models import CollectorProfile, RecyclerProfile
from core.models import Complaint
from decimal import Decimal
from datetime import date

User = get_user_model()

class RecyConnectWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Scrap Category
        self.category = ScrapCategory.objects.create(
            name='Test Metals',
            description='Test scrap metals',
            icon='bi-tools',
            base_rate_per_kg=Decimal('35.00'),
            min_rate_per_kg=Decimal('30.00'),
            max_rate_per_kg=Decimal('40.00'),
            unit='kg',
            is_active=True
        )

        # Users
        self.customer = User.objects.create_user(
            username='test_customer',
            password='password123',
            role=User.ROLE_CUSTOMER,
            email='cust@example.com',
            phone_number='1234567890',
            address='123 Green St',
            city='Green City',
            postal_code='110001'
        )

        self.collector = User.objects.create_user(
            username='test_collector',
            password='password123',
            role=User.ROLE_COLLECTOR,
            email='col@example.com',
            phone_number='9876543210'
        )
        self.collector_profile = self.collector.collector_profile
        self.collector_profile.is_verified = True
        self.collector_profile.service_area = 'Green City'
        self.collector_profile.save()

        self.recycler = User.objects.create_user(
            username='test_recycler',
            password='password123',
            role=User.ROLE_RECYCLER,
            email='rec@example.com'
        )
        self.recycler_profile = self.recycler.recycler_profile
        self.recycler_profile.company_name = 'Eco Metal Smelting'
        self.recycler_profile.save()

        self.admin = User.objects.create_superuser(
            username='test_admin',
            password='password123',
            email='admin@recyconnect.org',
            role=User.ROLE_ADMIN
        )

    def test_public_pages_load(self):
        """Verify public pages render correctly with 200 OK."""
        pages = [
            reverse('core:home'),
            reverse('core:about'),
            reverse('core:how_it_works'),
            reverse('core:contact'),
            reverse('core:privacy'),
            reverse('core:terms'),
            reverse('scrap:list'),
            reverse('accounts:login'),
            reverse('accounts:register'),
        ]
        for url in pages:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Page {url} failed to load.")

    def test_scrap_category_detail_and_api(self):
        """Verify scrap detail and rate JSON API."""
        response = self.client.get(reverse('scrap:detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Metals')

        api_response = self.client.get(reverse('scrap:api_rates'))
        self.assertEqual(api_response.status_code, 200)
        self.assertIn('categories', api_response.json())

    def test_customer_pickup_creation_and_cancellation(self):
        """Customer logs in, creates a pickup request, and cancels it."""
        self.client.login(username='test_customer', password='password123')

        # 1. Create Pickup
        pickup_data = {
            'category': self.category.id,
            'estimated_weight': '20.0',
            'preferred_date': date.today().isoformat(),
            'preferred_time_slot': '09:00 - 12:00',
            'pickup_address': '456 Oak Avenue',
            'city': 'Green City',
            'postal_code': '110001',
            'contact_phone': '9988776655',
            'notes': 'Segregated aluminum cans',
        }
        res = self.client.post(reverse('pickups:create'), pickup_data)
        self.assertEqual(res.status_code, 302)

        pickup = PickupRequest.objects.get(customer=self.customer)
        self.assertEqual(pickup.status, PickupRequest.STATUS_PENDING)
        self.assertEqual(pickup.estimated_weight, Decimal('20.0'))

        # 2. Cancel Pickup
        cancel_res = self.client.post(
            reverse('pickups:cancel', kwargs={'reference_id': pickup.reference_id}),
            {'cancellation_reason': 'Changed my mind'}
        )
        self.assertEqual(cancel_res.status_code, 302)
        pickup.refresh_from_db()
        self.assertEqual(pickup.status, PickupRequest.STATUS_CANCELLED)
        self.assertEqual(pickup.cancellation_reason, 'Changed my mind')

    def test_collector_accept_and_complete_workflow(self):
        """Collector accepts a pending request and completes it, generating a transaction."""
        # Create a pending pickup
        pickup = PickupRequest.objects.create(
            customer=self.customer,
            category=self.category,
            estimated_weight=Decimal('30.0'),
            pickup_address='789 Pine Road',
            city='Green City',
            postal_code='110001',
            preferred_date=date.today(),
            status=PickupRequest.STATUS_PENDING
        )

        # Login as collector
        self.client.login(username='test_collector', password='password123')

        # 1. Collector accepts pickup
        accept_res = self.client.post(reverse('pickups:accept', kwargs={'reference_id': pickup.reference_id}))
        self.assertEqual(accept_res.status_code, 302)
        pickup.refresh_from_db()
        self.assertEqual(pickup.status, PickupRequest.STATUS_ACCEPTED)
        self.assertEqual(pickup.assigned_collector, self.collector)

        # 2. Collector marks out for pickup
        inprog_res = self.client.post(reverse('pickups:update_status', kwargs={'reference_id': pickup.reference_id, 'new_status': 'in_progress'}))
        self.assertEqual(inprog_res.status_code, 302)
        pickup.refresh_from_db()
        self.assertEqual(pickup.status, PickupRequest.STATUS_IN_PROGRESS)

        # 3. Collector completes pickup with actual weight and agreed rate
        complete_data = {
            'actual_weight': '32.5',
            'agreed_rate_per_kg': '36.0',
            'payment_method': 'cash',
            'payment_status': 'PAID',
            'transaction_notes': 'Doorstep cash given',
        }
        complete_res = self.client.post(reverse('pickups:complete', kwargs={'reference_id': pickup.reference_id}), complete_data)
        self.assertEqual(complete_res.status_code, 302)

        pickup.refresh_from_db()
        self.assertEqual(pickup.status, PickupRequest.STATUS_COMPLETED)
        self.assertEqual(pickup.actual_weight, Decimal('32.5'))
        self.assertEqual(pickup.agreed_rate_per_kg, Decimal('36.0'))

        # Verify Transaction created and total calculated accurately
        txn = Transaction.objects.get(pickup=pickup)
        expected_total = Decimal('32.5') * Decimal('36.0')  # 1170.00
        self.assertEqual(txn.total_amount, expected_total)
        self.assertEqual(txn.payment_method, 'cash')
        self.assertEqual(txn.payment_status, 'PAID')

    def test_recycler_purchase_workflow(self):
        """Recycler submits purchase request and tracks order."""
        self.client.login(username='test_recycler', password='password123')

        purchase_data = {
            'category': self.category.id,
            'requested_quantity_kg': '500.0',
            'offered_price_per_kg': '38.0',
            'delivery_facility_address': 'Eco Metal Smelting Dock 3',
            'special_specifications': 'Sorted copper and brass only',
        }
        res = self.client.post(reverse('recyclers:purchase_create'), purchase_data)
        self.assertEqual(res.status_code, 302)

        order = PurchaseRequest.objects.get(recycler=self.recycler)
        self.assertEqual(order.status, PurchaseRequest.STATUS_PENDING)
        self.assertEqual(order.total_estimated_cost, Decimal('500.0') * Decimal('38.0'))

    def test_role_based_dashboard_dispatch(self):
        """Verify /dashboard/ redirects to the correct role-specific dashboard."""
        # Customer
        self.client.login(username='test_customer', password='password123')
        res = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(res, reverse('dashboard:customer'))

        # Collector
        self.client.login(username='test_collector', password='password123')
        res = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(res, reverse('dashboard:collector'))

        # Recycler
        self.client.login(username='test_recycler', password='password123')
        res = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(res, reverse('dashboard:recycler'))

        # Admin
        self.client.login(username='test_admin', password='password123')
        res = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(res, reverse('dashboard:admin'))
