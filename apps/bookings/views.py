from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.bookings.models import Booking
from apps.bookings.forms import BookingForm
from django.views.decorators.http import require_http_methods
from apps.tenants.models import Business, BusinessMember
from django.contrib import messages

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
