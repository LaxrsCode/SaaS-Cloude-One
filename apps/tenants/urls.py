from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    path('tenant/<slug:slug>/', views.tenant_preview, name='tenant_preview'),
]