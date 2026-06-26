from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.bookings.models import Booking, BookingBlock


ACTIVE_STATUSES = ('pending', 'confirmed', 'in_progress')


def calculate_end_datetime(start_datetime, service):
    return start_datetime + timedelta(minutes=service.duration)


def validate_datetime_order(start_datetime, end_datetime):
    if end_datetime <= start_datetime:
        raise ValidationError('La fecha de fin debe ser posterior a la de inicio.')


def validate_future_start(start_datetime, *, is_new):
    if is_new and start_datetime < timezone.now():
        raise ValidationError('No se pueden crear citas en el pasado.')


def validate_staff_for_service(staff, service):
    assigned_staff = service.staff.all()
    if assigned_staff.exists() and staff not in assigned_staff:
        raise ValidationError(
            f'El personal seleccionado no está asignado al servicio "{service.name}".'
        )


def validate_no_staff_overlap(staff, start_datetime, end_datetime, *, exclude_booking=None):
    qs = Booking.objects.filter(
        staff=staff,
        status__in=ACTIVE_STATUSES,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    )
    if exclude_booking is not None:
        qs = qs.exclude(pk=exclude_booking.pk)
    if qs.exists():
        raise ValidationError('El personal ya tiene una cita en ese horario.')


def validate_staff_availability(staff, start_datetime, end_datetime):
    from apps.tenants.models import AvailabilitySlot

    slots = AvailabilitySlot.objects.filter(
        staff=staff,
        day_of_week=start_datetime.weekday(),
        is_active=True,
    )
    if not slots.exists():
        return

    start_time = start_datetime.time()
    end_time = end_datetime.time()
    for slot in slots:
        if slot.start_time <= start_time and slot.end_time >= end_time:
            return

    raise ValidationError('El horario está fuera de la disponibilidad del personal.')


def validate_no_blocks(staff, start_datetime, end_datetime):
    if BookingBlock.objects.filter(
        staff=staff,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    ).exists():
        raise ValidationError('El horario está bloqueado para este personal.')


def validate_booking(
    *,
    staff,
    service,
    start_datetime,
    end_datetime,
    exclude_booking=None,
    is_new=True,
):
    validate_datetime_order(start_datetime, end_datetime)
    validate_future_start(start_datetime, is_new=is_new)
    validate_staff_for_service(staff, service)
    validate_no_staff_overlap(
        staff, start_datetime, end_datetime, exclude_booking=exclude_booking,
    )
    validate_staff_availability(staff, start_datetime, end_datetime)
    validate_no_blocks(staff, start_datetime, end_datetime)
