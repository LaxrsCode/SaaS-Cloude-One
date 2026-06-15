from django.db import models
from apps.tenants.models import Business, BusinessMember,Service
from apps.clients.models import Client
# Create your models here.

class BookingBlock(models.Model):
    staff           = models.ForeignKey(BusinessMember, related_name='blocks', on_delete=models.CASCADE)
    day_of_week     = models.IntegerField(choices=[(0,'Lun'),(1,'Mar'),(2,'Mie'),(3,'Jue'),(4,'Vie'),(5,'Sab'),(6,'Dom')])
    start_datetime  = models.DateTimeField()
    end_datetime    = models.DateTimeField()
    reason          = models.CharField(max_length=200, blank=True)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    business        = models.ForeignKey(Business, related_name='bookings', on_delete=models.CASCADE)
    service         = models.ForeignKey(Service, on_delete=models.PROTECT)
    staff           = models.ForeignKey(BusinessMember, on_delete=models.PROTECT)
    client          = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='bookings')
    start_datetime  = models.DateTimeField()
    end_datetime    = models.DateTimeField()
    status          = models.CharField(choices=STATUS_CHOICES, default='pending')
    google_event_id = models.CharField(max_length=255, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)



