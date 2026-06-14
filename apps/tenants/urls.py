from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    path('landing/<slug:slug>/', views.tenant_preview, name='tenant_preview'),
    path('register/', views.tenant_register, name='tenant_register'),
    path('', views.tenant_list, name='tenant_list'),
    path('<slug:slug>/settings/', views.tenant_settings, name='tenant_settings'),
    path('<slug:slug>/members/', views.tenant_members, name='tenant_members'),
    path('<slug:slug>/members/invite/', views.tenant_member_invite, name='tenant_member_invite'),
]