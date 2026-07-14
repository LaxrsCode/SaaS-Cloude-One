# apps/tenants/public_urls.py
from django.urls import path
from . import views

app_name = 'tenant_public'

urlpatterns = [
    path('', views.public_landing_page, name='public_landing'),
    # path('reservar/', views.booking, name='booking'),  # futuro
]