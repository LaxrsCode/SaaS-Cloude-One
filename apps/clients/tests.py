from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.tenants.models import Business

from .models import Client, ClientNote

User = get_user_model()


class ClientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='owner@test.com', password='testpass123')
        self.business = Business.objects.create(name='Test Salon', slug='test-salon', owner=self.user)

    def test_create_client(self):
        client = Client.objects.create(business=self.business, first_name='John', last_name='Doe')
        self.assertEqual(str(client), 'John Doe')
        self.assertEqual(client.total_visits, 0)

    def test_add_note(self):
        client = Client.objects.create(business=self.business, first_name='Jane')
        note = ClientNote.objects.create(client=client, author=self.user, content='Test note')
        self.assertEqual(str(note), f'Note on Jane by {self.user}')
