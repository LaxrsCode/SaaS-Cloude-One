from django.db import models
from django.conf import settings
# Create your models here.

class Business(models.Model):
    name            = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(unique=True, blank=True) 
    subdomain       = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description     = models.TextField(blank=True)
    category        = models.CharField(
        choices=[
            ('barberia', 'Barberia'),
            ('salon', 'Salon'),
            ('spa', 'Spa'),
            ('clinica', 'Clinica'),
            ('gimnasio', 'Gimnasio'),
            ('restaurante', 'Restaurante'),
            ('consultorio', 'Consultorio'),
            ('tatuador', 'Tatuador'),
            ('entrenador', 'Entrenador'),
            ('otro', 'Otro'),
        ],
        default='otro',
    )
    owner           = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_businesses', on_delete=models.CASCADE)
    subscription_tier = models.CharField(
        choices=[
            ('trial', 'Trial'),
            ('pro', 'Pro'),
        ],
        default='trial',
    )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return self.name


class BusinessSettings(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='settings')
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#666666')
    font_family = models.CharField(max_length=100, default='Space Grotesk')
    phone_contact = models.CharField(max_length=15, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    address_contact = models.TextField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    working_hours = models.JSONField(default=dict)
    google_maps_url = models.URLField(blank=True, null=True)
    google_calendar_enabled = models.BooleanField(default=False)
    google_calendar_id = models.CharField( max_length=255, blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BusinessMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    business    = models.ForeignKey(Business, related_name='members', on_delete=models.CASCADE)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='business_memberships', on_delete=models.CASCADE)
    role        = models.CharField(choices=ROLE_CHOICES, default='staff')
    is_active   = models.BooleanField(default=True)
    joined_at   = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.business.name}"
