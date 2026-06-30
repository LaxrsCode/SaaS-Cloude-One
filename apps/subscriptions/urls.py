from django.urls import path

from . import views
from . import webhooks

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_page, name='subscription_page'),
    path('checkout/', views.create_checkout_session, name='create_checkout'),
    path('portal/', views.customer_portal, name='customer_portal'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
]
