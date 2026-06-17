from django.db import models

from apps.clients.models import Client


class Service(models.Model):
    business = models.ForeignKey(
        'tenants.Business',
        on_delete=models.CASCADE,
        related_name='services',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.business.name})'


class Staff(models.Model):
    business = models.ForeignKey(
        'tenants.Business',
        on_delete=models.CASCADE,
        related_name='staff',
    )
    member = models.OneToOneField(
        'tenants.BusinessMember',
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        ordering = ['member__user__first_name']

    def __str__(self):
        return f'{self.member.user.email} - {self.business.name}'


class StaffService(models.Model):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='service_assignments',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
    )
    duration = models.IntegerField(help_text='Override duration in minutes')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Staff Service'
        verbose_name_plural = 'Staff Services'
        unique_together = ('staff', 'service')

    def __str__(self):
        return f'{self.staff} - {self.service}'


class AvailabilitySlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='availability',
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Availability Slot'
        verbose_name_plural = 'Availability Slots'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f'{self.staff} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class BookingBlock(models.Model):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='blocks',
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Booking Block'
        verbose_name_plural = 'Booking Blocks'
        ordering = ['start_datetime']

    def __str__(self):
        return f'Block {self.staff} - {self.start_datetime.date()}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    business = models.ForeignKey(
        'tenants.Business',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)
    google_event_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-start_datetime']

    def __str__(self):
        return f'{self.client} - {self.service} ({self.get_status_display()})'
