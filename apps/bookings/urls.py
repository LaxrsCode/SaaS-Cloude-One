from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('<slug:slug>/tenants/bookings_list',views.booking_list_owner,name='booking_list'),
    path('<slug:slug>/tenants/bookings_list_staff',views.booking_list_staff,name='booking_list_staff'),
    path('<slug:slug>/tenants/bookings_form',views.booking_create,name='booking_create'),
    path('<slug:slug>/tenants/bookings/<int:booking_id>/edit',views.booking_edit,name='booking_edit'),
    path('<slug:slug>/tenants/bookings/<int:booking_id>/delete',views.booking_delete,name='booking_edit'),
]