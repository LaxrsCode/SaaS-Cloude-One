from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.tenants.models import Business

from .models import Client, ClientNote


@login_required
@require_http_methods(['GET'])
def client_list(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    clients = business.clients.all()
    search = request.GET.get('q', '').strip()
    if search:
        clients = clients.filter(
            models.Q(first_name__icontains=search)
            | models.Q(last_name__icontains=search)
            | models.Q(email__icontains=search)
            | models.Q(phone__icontains=search)
        )
    return render(request, 'clients/client_list.html', {
        'business': business,
        'clients': clients,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def client_create(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    if request.method == 'POST':
        client = Client.objects.create(
            business=business,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'Client {client.first_name} created.')
        return redirect('clients:client_list', business_slug=business.slug)
    return render(request, 'clients/client_form.html', {'business': business})


@login_required
@require_http_methods(['GET', 'POST'])
def client_detail(request, business_slug, client_id):
    business = get_object_or_404(Business, slug=business_slug)
    client = get_object_or_404(Client, id=client_id, business=business)
    if request.method == 'POST' and request.POST.get('note'):
        ClientNote.objects.create(
            client=client,
            author=request.user,
            content=request.POST['note'],
        )
        messages.success(request, 'Note added.')
        return redirect('clients:client_detail', business_slug=business.slug, client_id=client.id)
    notes = client.client_notes.select_related('author').all()
    bookings = client.bookings.select_related('service', 'staff').order_by('-start_datetime')
    return render(request, 'clients/client_detail.html', {
        'business': business,
        'client': client,
        'notes': notes,
        'bookings': bookings,
    })


@login_required
@require_http_methods(['POST'])
def client_edit(request, business_slug, client_id):
    business = get_object_or_404(Business, slug=business_slug)
    client = get_object_or_404(Client, id=client_id, business=business)
    client.first_name = request.POST.get('first_name', client.first_name)
    client.last_name = request.POST.get('last_name', client.last_name)
    client.email = request.POST.get('email', client.email)
    client.phone = request.POST.get('phone', client.phone)
    client.notes = request.POST.get('notes', client.notes)
    client.save()
    messages.success(request, 'Client updated.')
    return redirect('clients:client_detail', business_slug=business.slug, client_id=client.id)


@login_required
@require_http_methods(['POST'])
def client_delete(request, business_slug, client_id):
    business = get_object_or_404(Business, slug=business_slug)
    client = get_object_or_404(Client, id=client_id, business=business)
    client.delete()
    messages.success(request, 'Client deleted.')
    return redirect('clients:client_list', business_slug=business.slug)
