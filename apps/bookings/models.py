from django.db import models
from apps.tenants.models import Business, BusinessMember,Service
from apps.clients.models import Client
from django.utils import timezone
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
    notes = models.TextField(blank=True, default='')
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_history = models.JSONField(default=list, blank=True)
    google_event_id = models.CharField(max_length=255, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def change_status(self, new_status):
        valid = {code for code, _label in self.STATUS_CHOICES}
        if new_status not in valid:
            raise ValueError(f'Estado inválido: {new_status}')
        old_status = self.status
        if old_status == new_status:
            return self
        now = timezone.now()
        history = list(self.status_history or [])
        history.append({'from': old_status, 'to': new_status, 'at': now.isoformat()})
        self.status = new_status
        self.status_changed_at = now
        self.status_history = history
        self.save(update_fields=['status', 'status_changed_at', 'status_history', 'updated_at'])
        return self



