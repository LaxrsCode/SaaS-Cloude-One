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
    path('<slug:slug>/services/', views.service_list, name='service_list'),
    path('<slug:slug>/services/create/', views.service_create, name='service_create'),
    path('<slug:slug>/services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('<slug:slug>/services/<int:service_id>/delete/', views.service_disable, name='service_delete'),
]