from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='testpass123')

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            type='system_announcement',
            title='Welcome!',
            message='Welcome to the platform.',
        )
        self.assertEqual(str(notification), f'Welcome! - {self.user.email}')
        self.assertFalse(notification.is_read)

    def test_unread_count(self):
        Notification.objects.create(user=self.user, type='system_announcement', title='Test', message='Msg')
        self.assertEqual(self.user.notifications.filter(is_read=False).count(), 1)
