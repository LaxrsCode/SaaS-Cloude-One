from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.clients.models import Client
from apps.tenants.models import Business, BusinessMember

from .models import Booking, Service, Staff

User = get_user_model()


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='owner@test.com', password='testpass123')
        self.business = Business.objects.create(name='Test Salon', slug='test-salon', owner=self.user)
        self.member = BusinessMember.objects.create(business=self.business, user=self.user, role='owner')
        self.service = Service.objects.create(business=self.business, name='Haircut', duration=30, price=25.00)
        self.staff = Staff.objects.create(business=self.business, member=self.member)
        self.client_obj = Client.objects.create(business=self.business, first_name='John', last_name='Doe')

    def test_create_service(self):
        self.assertEqual(str(self.service), 'Haircut (Test Salon)')
        self.assertTrue(self.service.is_active)

    def test_create_staff(self):
        self.assertTrue(self.staff.is_active)

    def test_create_booking(self):
        from django.utils import timezone
        start = timezone.now()
        end = start + timezone.timedelta(minutes=30)
        booking = Booking.objects.create(
            business=self.business,
            service=self.service,
            staff=self.staff,
            client=self.client_obj,
            start_datetime=start,
            end_datetime=end,
        )
        self.assertEqual(booking.status, 'pending')
        self.assertTrue(str(booking).startswith('John Doe'))
