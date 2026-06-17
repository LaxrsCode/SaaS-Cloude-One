from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.business_list, name='business_list'),
    path('create/', views.business_create, name='business_create'),
    path('<slug:slug>/', views.business_detail, name='business_detail'),
    path('<slug:slug>/members/<int:member_id>/remove/', views.business_remove_member, name='business_remove_member'),
]
