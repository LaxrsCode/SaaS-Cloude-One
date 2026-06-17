from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('<slug:business_slug>/bookings/', views.booking_list, name='booking_list'),
    path('<slug:business_slug>/bookings/create/', views.booking_create, name='booking_create'),
    path('<slug:business_slug>/bookings/<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<slug:business_slug>/bookings/<int:booking_id>/status/', views.booking_update_status, name='booking_update_status'),
    path('<slug:business_slug>/services/', views.service_list, name='service_list'),
    path('<slug:business_slug>/services/create/', views.service_create, name='service_create'),
    path('<slug:business_slug>/services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('<slug:business_slug>/services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
    path('<slug:business_slug>/staff/', views.staff_list, name='staff_list'),
    path('<slug:business_slug>/staff/create/', views.staff_create, name='staff_create'),
    path('<slug:business_slug>/staff/<int:staff_id>/toggle/', views.staff_toggle_active, name='staff_toggle_active'),
    path('<slug:business_slug>/staff/<int:staff_id>/availability/', views.availability_manage, name='availability_manage'),
]
