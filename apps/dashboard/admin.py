from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import SubscriptionPlan
from django.utils.translation import gettext_lazy as _


class DashboardAdminSite(AdminSite):
    site_header = _('Dashboard Administration')
    site_title = _('Dashboard Admin')
    index_title = _('Welcome to the Dashboard Admin')

dashboard_admin_site = DashboardAdminSite(name='dashboard_admin')

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'interval', 'trial_days', 'stripe_price_id', 'is_active')
    list_filter = ('is_active', 'interval')
    search_fields = ('name', 'slug', 'stripe_price_id')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Plan Info', {
            'fields': ('name', 'slug', 'description', 'price', 'interval', 'trial_days', 'features', 'is_active')
        }),
        ('Stripe Configuration', {
            'fields': ('stripe_price_id', 'stripe_product_id'),
            'classes': ('wide',),
            'description': 'Pega aquí los IDs de Stripe Dashboard. El plan necesita stripe_price_id para cobrar.',
        }),
    )