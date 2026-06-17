from django.urls import path

from . import views

app_name = 'clients'

urlpatterns = [
    path('<slug:business_slug>/', views.client_list, name='client_list'),
    path('<slug:business_slug>/create/', views.client_create, name='client_create'),
    path('<slug:business_slug>/<int:client_id>/', views.client_detail, name='client_detail'),
    path('<slug:business_slug>/<int:client_id>/edit/', views.client_edit, name='client_edit'),
    path('<slug:business_slug>/<int:client_id>/delete/', views.client_delete, name='client_delete'),
]
