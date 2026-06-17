from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking_new', 'New Booking Received'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('subscription_renewed', 'Subscription Renewed'),
        ('trial_expiring', 'Trial Expiring Soon'),
        ('system_announcement', 'System Announcement'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    business = models.ForeignKey(
        'tenants.Business',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.email}'


class EmailReminder(models.Model):
    TYPE_CHOICES = [
        ('confirmation', 'Booking Confirmation'),
        ('reminder_24h', '24h Reminder'),
        ('reminder_1h', '1h Reminder'),
        ('cancelled', 'Cancellation Notice'),
        ('completed', 'Completion Notice'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='email_reminders',
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Email Reminder'
        verbose_name_plural = 'Email Reminders'
        unique_together = ('booking', 'type')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()} - {self.recipient_email} ({self.get_status_display()})'
