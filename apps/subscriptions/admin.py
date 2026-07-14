from django.contrib import admin

from .models import StripeCustomer, Subscription, WebhookEvent


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    readonly_fields = ('stripe_subscription_id', 'status', 'created_at', 'updated_at')
    can_delete = False


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'latest_subscription_status', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at', 'latest_subscription_status')
    inlines = [SubscriptionInline]
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Stripe Info', {
            'fields': ('stripe_customer_id', 'latest_subscription_status')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Subscription status')
    def latest_subscription_status(self, obj):
        sub = obj.subscriptions.order_by('-created_at').first()
        return sub.status if sub else '—'

    def has_add_permission(self, request):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer', 'status', 'plan', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'processed_at')
    search_fields = ('stripe_event_id',)
    readonly_fields = ('stripe_event_id', 'processed_at')

    def has_add_permission(self, request):
        return False
