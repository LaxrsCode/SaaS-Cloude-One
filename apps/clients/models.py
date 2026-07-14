from django.db import models
from apps.tenants.models import Business
# Create your models here.

class Client(models.Model):
    business        = models.ForeignKey(Business, related_name='clients', on_delete=models.CASCADE)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100, blank=True)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    notes           = models.TextField(blank=True)
    total_visits    = models.IntegerField(default=0)
    last_visit      = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)