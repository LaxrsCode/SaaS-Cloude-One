from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()

class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    #stripe_subscription_id = models.CharField(max_length=255, blank=True, default='')
    #subscription_status = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        sub = self.subscriptions.order_by('-created_at').first()
        status = sub.status if sub else 'no subscription'
        return f"{self.user.email} - {status}"


# añadir la suscripcion

# Subscription guarda CADA relación contractual
class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    stripe_customer = models.ForeignKey(
        StripeCustomer,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    plan = models.ForeignKey(
        'dashboard.SubscriptionPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stripe_subscriptions'
    )
    status = models.CharField(max_length=50)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.status} ({self.stripe_subscription_id})"

    @property
    def is_active(self):
        return self.status in {'active', 'trialing', 'past_due'}

    @property
    def is_trialing(self):
        return self.status == 'trialing'


class WebhookEvent(models.Model):
    """Registro de eventos de Stripe ya procesados (idempotencia)."""
    stripe_event_id = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-processed_at']
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'

    def __str__(self):
        return self.stripe_event_id