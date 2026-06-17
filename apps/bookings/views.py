from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.clients.models import Client
from apps.tenants.models import Business, BusinessMember

from .models import (
    AvailabilitySlot,
    Booking,
    Service,
    Staff,
)


@login_required
@require_http_methods(['GET'])
def booking_list(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    date_str = request.GET.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = timezone.now().date()
    prev_date = date - timedelta(days=1)
    next_date = date + timedelta(days=1)
    bookings = business.bookings.filter(start_datetime__date=date).select_related('client', 'service', 'staff')
    return render(request, 'bookings/booking_list.html', {
        'business': business,
        'bookings': bookings,
        'current_date': date,
        'prev_date': prev_date,
        'next_date': next_date,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def booking_create(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    services = business.services.filter(is_active=True)
    staff_members = business.staff.filter(is_active=True)
    clients = business.clients.all()

    if request.method == 'POST':
        service = get_object_or_404(Service, id=request.POST['service'], business=business)
        staff = get_object_or_404(Staff, id=request.POST['staff'], business=business)
        client = get_object_or_404(Client, id=request.POST['client'], business=business)
        start_str = request.POST.get('start_datetime')
        if not start_str:
            messages.error(request, 'Start datetime is required.')
            return render(request, 'bookings/booking_form.html', {
                'business': business, 'services': services,
                'staff_members': staff_members, 'clients': clients,
            })
        try:
            start_dt = datetime.fromisoformat(start_str)
        except ValueError:
            start_dt = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
        if timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt)
        duration = service.duration
        end_dt = start_dt + timedelta(minutes=duration)

        Booking.objects.create(
            business=business,
            service=service,
            staff=staff,
            client=client,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status='confirmed',
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Booking created.')
        return redirect('bookings:booking_list', business_slug=business.slug)

    return render(request, 'bookings/booking_form.html', {
        'business': business,
        'services': services,
        'staff_members': staff_members,
        'clients': clients,
    })


@login_required
@require_http_methods(['POST'])
def booking_cancel(request, business_slug, booking_id):
    business = get_object_or_404(Business, slug=business_slug)
    booking = get_object_or_404(Booking, id=booking_id, business=business)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled.')
    return redirect('bookings:booking_list', business_slug=business.slug)


@login_required
@require_http_methods(['POST'])
def booking_update_status(request, business_slug, booking_id):
    business = get_object_or_404(Business, slug=business_slug)
    booking = get_object_or_404(Booking, id=booking_id, business=business)
    new_status = request.POST.get('status', '')
    valid_statuses = [s[0] for s in Booking.STATUS_CHOICES]
    if new_status in valid_statuses:
        booking.status = new_status
        booking.save()
        messages.success(request, f'Booking status updated to {booking.get_status_display()}.')
    return redirect('bookings:booking_list', business_slug=business.slug)


@login_required
@require_http_methods(['GET'])
def service_list(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    services = business.services.all()
    return render(request, 'bookings/service_list.html', {
        'business': business,
        'services': services,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def service_create(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    if request.method == 'POST':
        Service.objects.create(
            business=business,
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            duration=int(request.POST['duration']),
            price=request.POST['price'],
        )
        messages.success(request, 'Service created.')
        return redirect('bookings:service_list', business_slug=business.slug)
    return render(request, 'bookings/service_form.html', {'business': business})


@login_required
@require_http_methods(['POST'])
def service_edit(request, business_slug, service_id):
    business = get_object_or_404(Business, slug=business_slug)
    service = get_object_or_404(Service, id=service_id, business=business)
    service.name = request.POST.get('name', service.name)
    service.description = request.POST.get('description', service.description)
    service.duration = int(request.POST.get('duration', service.duration))
    service.price = request.POST.get('price', service.price)
    service.is_active = request.POST.get('is_active') == 'on'
    service.save()
    messages.success(request, 'Service updated.')
    return redirect('bookings:service_list', business_slug=business.slug)


@login_required
@require_http_methods(['POST'])
def service_delete(request, business_slug, service_id):
    business = get_object_or_404(Business, slug=business_slug)
    service = get_object_or_404(Service, id=service_id, business=business)
    service.delete()
    messages.success(request, 'Service deleted.')
    return redirect('bookings:service_list', business_slug=business.slug)


@login_required
@require_http_methods(['GET'])
def staff_list(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    staff_members = business.staff.select_related('member__user').all()
    available_members = business.members.filter(is_active=True).exclude(
        staff_profile__isnull=False
    )
    return render(request, 'bookings/staff_list.html', {
        'business': business,
        'staff_members': staff_members,
        'available_members': available_members,
    })


@login_required
@require_http_methods(['POST'])
def staff_create(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    member_id = request.POST.get('member_id')
    member = get_object_or_404(BusinessMember, id=member_id, business=business)
    if Staff.objects.filter(member=member).exists():
        messages.warning(request, 'This member is already a staff member.')
    else:
        Staff.objects.create(business=business, member=member)
        messages.success(request, 'Staff member added.')
    return redirect('bookings:staff_list', business_slug=business.slug)


@login_required
@require_http_methods(['POST'])
def staff_toggle_active(request, business_slug, staff_id):
    business = get_object_or_404(Business, slug=business_slug)
    staff = get_object_or_404(Staff, id=staff_id, business=business)
    staff.is_active = not staff.is_active
    staff.save()
    return redirect('bookings:staff_list', business_slug=business.slug)


@login_required
@require_http_methods(['GET', 'POST'])
def availability_manage(request, business_slug, staff_id):
    business = get_object_or_404(Business, slug=business_slug)
    staff = get_object_or_404(Staff, id=staff_id, business=business)
    if request.method == 'POST':
        days = request.POST.getlist('day_of_week')
        start_times = request.POST.getlist('start_time')
        end_times = request.POST.getlist('end_time')
        staff.availability.all().delete()
        for day, start, end in zip(days, start_times, end_times, strict=False):
            if start and end:
                AvailabilitySlot.objects.create(
                    staff=staff,
                    day_of_week=int(day),
                    start_time=start,
                    end_time=end,
                )
        messages.success(request, 'Availability updated.')
        return redirect('bookings:staff_list', business_slug=business.slug)
    slots = staff.availability.filter(is_active=True).order_by('day_of_week', 'start_time')
    return render(request, 'bookings/availability_form.html', {
        'business': business,
        'staff': staff,
        'slots': slots,
        'day_choices': AvailabilitySlot.DAY_CHOICES,
    })
