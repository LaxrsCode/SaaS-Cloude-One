from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.bookings.forms import BookingForm, BookingRequestForm
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.notifications.models import Notification
from apps.tenants.models import Business, BusinessMember

# ---- Views Gestion de Citas ----
@login_required
@require_http_methods(['GET'])
def booking_list_owner(request,slug):
    business = get_object_or_404(Business,owner=request.user,slug=slug,is_active=True)
    bookings = business.bookings.select_related('service', 'staff', 'client').order_by('start_datetime')
    return render(request,'tenants/bookings_list.html',{
        'business': business,
        'bookings': bookings,
    })

@login_required
@require_http_methods(['GET'])
def booking_list_staff(request,slug):
    business = get_object_or_404(Business,slug=slug,is_active=True)
    staff = business.members.filter(business=business,user=request.user,role='staff',is_active=True)
    qs = Booking.objects.filter(staff=staff, business=business).select_related(
    'service', 'client'
    ).order_by('start_datetime')
    return render(request,'tenants/bookings_list_staff.html',{
        'staff': staff,
        'queryset': qs,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def booking_create(request, slug):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)

    if request.method == 'POST':
        form = BookingForm(request.POST, business=business)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Cita "{booking}" creado.')
            return redirect('tenants:bookings_list', slug=business.slug)
    else:
        form = BookingForm(business=business)

    return render(request, 'tenants/booking_form.html', {
        'form': form,
        'business': business,
        'is_edit': False,
    })

@login_required
@require_http_methods(['GET', 'POST'])
def booking_edit(request, slug, booking_id):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    booking = get_object_or_404(Booking, pk=booking_id, business=business)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking ,business=business)
        if form.is_valid():
            booking= form.save()
            messages.success(request, f'Cita "{booking}" actualizado.')
            return redirect('tenants:bookings_list', slug=business.slug)
    else:
        form = BookingForm(instance=booking, business=business)

    return render(request, 'tenants/booking_form.html', {
        'form': form,
        'business': business,
        'booking': booking,
        'is_edit': True,
    })

@login_required
@require_http_methods(['POST'])
def booking_delete(request, slug, booking_id):
    business = get_object_or_404(Business, slug=slug, owner=request.user, is_active=True)
    booking = get_object_or_404(Booking, pk=booking_id, business=business)
    booking.delete()
    messages.success(request,f'Cita {booking} eliminada')
    return redirect('tenants:bookings_list', slug=business.slug)

def _can_manage(user, business):
    if business.owner_id == user.id:
        return True
    return BusinessMember.objects.filter(business=business, user=user, is_active=True).exists()


def _notify_owners(business, booking):
    for member in business.members.filter(is_active=True):
        Notification.objects.create(
            user=member.user,
            business=business,
            type='booking_new',
            title='Nueva solicitud de reserva',
            message=(
                f'{booking.client.first_name} {booking.client.last_name} solicita '
                f'"{booking.service.name}" para el {booking.start_datetime:%d/%m/%Y %H:%M}.'
            ),
            link=f'/bookings/{business.slug}/requests/',
        )


def _notify_request_result(business, booking, result):
    target = getattr(booking.client, 'user', None)
    if target is None:
        return
    Notification.objects.create(
        user=target,
        business=business,
        type='booking_new',
        title=f'Solicitud {result}',
        message=f'Tu solicitud para "{booking.service.name}" fue {result}.',
    )


@login_required
@require_http_methods(['GET', 'POST'])
def booking_request(request, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)

    if request.method == 'POST':
        form = BookingRequestForm(request.POST, business=business)
        if form.is_valid():
            client = Client.objects.filter(business=business, email=request.user.email).first()
            if client is None:
                client, _ = Client.objects.get_or_create(
                    business=business,
                    user=request.user,
                    defaults={
                        'first_name': request.user.first_name or request.user.email.split('@')[0],
                        'last_name': request.user.last_name or '',
                        'email': request.user.email,
                        'phone': request.user.phone_number or '',
                    },
                )
            if not client.email:
                client.email = request.user.email
                client.save(update_fields=['email', 'updated_at'])

            booking = Booking.objects.create(
                business=business,
                service=form.cleaned_data['service'],
                staff=form.cleaned_data['staff'],
                client=client,
                start_datetime=form.cleaned_data['start_datetime'],
                end_datetime=form.cleaned_data['end_datetime'],
                status='pending',
                notes=form.cleaned_data.get('notes', ''),
            )
            _notify_owners(business, booking)
            messages.success(request, 'Solicitud enviada. Queda pendiente de confirmación por el negocio.')
            return redirect('bookings:booking_request_success', slug=business.slug)
    else:
        form = BookingRequestForm(business=business)

    return render(request, 'bookings/request_form.html', {
        'form': form,
        'business': business,
    })


@login_required
@require_http_methods(['GET'])
def booking_request_success(request, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    return render(request, 'bookings/request_success.html', {'business': business})


@login_required
@require_http_methods(['GET'])
def requests_list(request, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    if not _can_manage(request.user, business):
        messages.error(request, 'No tienes permisos para gestionar estas solicitudes.')
        return redirect('dashboard:home')

    requests = (
        Booking.objects.filter(business=business, status='pending')
        .select_related('service', 'staff', 'client')
        .order_by('start_datetime')
    )
    # Consulta SQL equivalente (referencia):
    # SELECT b.*, c.email AS client_email, c.phone AS client_phone
    # FROM bookings_booking b
    # JOIN clients_client c ON c.id = b.client_id
    # WHERE b.business_id = %s AND b.status = 'pending'
    # ORDER BY b.start_datetime;
    return render(request, 'bookings/requests_list.html', {
        'business': business,
        'requests': requests,
    })


@login_required
@require_POST
def request_accept(request, slug, booking_id):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    if not _can_manage(request.user, business):
        messages.error(request, 'No tienes permisos para gestionar estas solicitudes.')
        return redirect('dashboard:home')
    booking = get_object_or_404(Booking, pk=booking_id, business=business)
    booking.change_status('confirmed')
    booking.client.refresh_visits()
    _notify_request_result(business, booking, 'confirmada')
    messages.success(request, f'Solicitud confirmada para {booking.client.first_name}.')
    return redirect('bookings:requests_list', slug=business.slug)


@login_required
@require_POST
def request_reject(request, slug, booking_id):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    if not _can_manage(request.user, business):
        messages.error(request, 'No tienes permisos para gestionar estas solicitudes.')
        return redirect('dashboard:home')
    booking = get_object_or_404(Booking, pk=booking_id, business=business)
    booking.change_status('cancelled')
    _notify_request_result(business, booking, 'rechazada')
    messages.success(request, f'Solicitud de {booking.client.first_name} rechazada.')
    return redirect('bookings:requests_list', slug=business.slug)


@login_required
@require_POST
def request_delete(request, slug, booking_id):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    if not _can_manage(request.user, business):
        messages.error(request, 'No tienes permisos para gestionar estas solicitudes.')
        return redirect('dashboard:home')
    booking = get_object_or_404(Booking, pk=booking_id, business=business)
    booking.delete()
    messages.success(request, 'Solicitud eliminada.')
    return redirect('bookings:requests_list', slug=business.slug)