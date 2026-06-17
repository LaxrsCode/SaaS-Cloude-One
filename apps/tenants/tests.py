from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Business, BusinessMember, BusinessSettings

User = get_user_model()


class BusinessModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='owner@test.com', password='testpass123')

    def test_create_business(self):
        business = Business.objects.create(name='Test Salon', slug='test-salon', owner=self.user)
        self.assertEqual(str(business), 'Test Salon')
        self.assertEqual(business.subscription_tier, 'free')
        self.assertTrue(business.is_active)

    def test_create_business_creates_settings(self):
        business = Business.objects.create(name='Test', slug='test', owner=self.user)
        BusinessSettings.objects.create(business=business)
        self.assertEqual(business.settings.timezone, 'America/Santo_Domingo')

    def test_add_member(self):
        business = Business.objects.create(name='Test', slug='test', owner=self.user)
        member = BusinessMember.objects.create(business=business, user=self.user, role='owner')
        self.assertEqual(str(member), f'{self.user.email} - Test (owner)')


class BusinessViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='testpass123')
        self.client.force_login(self.user)

    def test_business_list_accessible(self):
        response = self.client.get('/business/')
        self.assertEqual(response.status_code, 200)

    def test_business_create_redirects(self):
        response = self.client.post('/business/create/', {'name': 'New Biz', 'category': 'salon'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Business.objects.filter(name='New Biz').exists())
