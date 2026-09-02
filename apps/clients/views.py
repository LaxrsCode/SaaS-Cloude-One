from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.tenants.models import Business, BusinessMember

from .forms import ClientForm
from .models import Client, ClientNote


def _can_manage(user, business):
    if business.owner_id == user.id:
        return True
    return BusinessMember.objects.filter(business=business, user=user, is_active=True).exists()


def _get_business(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug, is_active=True)
    if not _can_manage(request.user, business):
        messages.error(request, 'No tienes permisos para acceder a este negocio.')
        return None
    return business


@login_required
@require_http_methods(['GET'])
def client_list(request, business_slug):
    business = _get_business(request, business_slug)
    if business is None:
        return redirect('dashboard:home')

    clients = Client.objects.filter(business=business).order_by('first_name')
    q = request.GET.get('q', '').strip()
    if q:
        clients = clients.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
        )
    return render(request, 'clients/client_list.html', {'business': business, 'clients': clients})


@login_required
@require_http_methods(['GET', 'POST'])
def client_create(request, business_slug):
    business = _get_business(request, business_slug)
    if business is None:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.business = business
            client.save()
            messages.success(request, f'Cliente "{client.full_name}" creado.')
            return redirect('clients:client_detail', business_slug=business.slug, client_id=client.id)
    else:
        form = ClientForm()

    return render(request, 'clients/client_form.html', {'form': form, 'business': business})


@login_required
@require_http_methods(['GET', 'POST'])
def client_detail(request, business_slug, client_id):
    business = _get_business(request, business_slug)
    if business is None:
        return redirect('dashboard:home')
    client = get_object_or_404(Client, pk=client_id, business=business)

    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        if note:
            ClientNote.objects.create(client=client, author=request.user, content=note)
        messages.success(request, 'Nota añadida.')
        return redirect('clients:client_detail', business_slug=business.slug, client_id=client.id)

    return render(request, 'clients/client_detail.html', {
        'client': client,
        'business': business,
        'bookings': client.booking_history(),
        'notes': client.client_notes.select_related('author').all(),
    })


@login_required
@require_POST
def client_edit(request, business_slug, client_id):
    business = _get_business(request, business_slug)
    if business is None:
        return redirect('dashboard:home')
    client = get_object_or_404(Client, pk=client_id, business=business)

    form = ClientForm(request.POST, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado.')
    else:
        messages.error(request, 'No se pudo actualizar el cliente: revisa los campos.')
    return redirect('clients:client_detail', business_slug=business.slug, client_id=client.id)


@login_required
@require_POST
def client_delete(request, business_slug, client_id):
    business = _get_business(request, business_slug)
    if business is None:
        return redirect('dashboard:home')
    client = get_object_or_404(Client, pk=client_id, business=business)

    try:
        client.delete()
        messages.success(request, 'Cliente eliminado.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar: el cliente tiene citas registradas. Cancela sus citas primero.')
    return redirect('clients:client_list', business_slug=business.slug)