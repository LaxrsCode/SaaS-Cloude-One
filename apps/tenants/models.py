from django.conf import settings
from django.db import models


class Business(models.Model):
    CATEGORY_CHOICES = [
        ('barberia', 'Barbería'),
        ('salon', 'Salón'),
        ('spa', 'Spa'),
        ('clinica', 'Clínica'),
        ('gimnasio', 'Gimnasio'),
        ('restaurante', 'Restaurante'),
        ('consultorio', 'Consultorio'),
        ('tatuador', 'Tatuador'),
        ('entrenador', 'Entrenador'),
        ('otro', 'Otro'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subdomain = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='otro')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_businesses',
    )
    subscription_tier = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('business', 'Business')],
        default='free',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return self.name


class BusinessSettings(models.Model):
    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name='settings',
    )
    logo = models.ImageField(upload_to='businesses/logos/', blank=True)
    cover_image = models.ImageField(upload_to='businesses/covers/', blank=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#666666')
    font_family = models.CharField(max_length=100, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    website = models.URLField(blank=True)
    social_facebook = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_tiktok = models.URLField(blank=True)
    working_hours = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='America/Santo_Domingo')
    currency = models.CharField(max_length=3, default='DOP')
    google_calendar_enabled = models.BooleanField(default=False)
    google_calendar_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'

    def __str__(self):
        return f'Settings for {self.business.name}'


class BusinessMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('business', 'user')
        verbose_name = 'Business Member'
        verbose_name_plural = 'Business Members'

    def __str__(self):
        return f'{self.user.email} - {self.business.name} ({self.role})'
