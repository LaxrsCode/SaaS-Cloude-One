from django.contrib import admin

from .models import (
    AvailabilitySlot,
    Booking,
    BookingBlock,
    Service,
    Staff,
    StaffService,
)


class StaffServiceInline(admin.TabularInline):
    model = StaffService
    extra = 1


class AvailabilitySlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'duration', 'price', 'is_active']
    list_filter = ['business', 'is_active']
    search_fields = ['name', 'business__name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['member', 'business', 'is_active']
    list_filter = ['business', 'is_active']
    inlines = [StaffServiceInline, AvailabilitySlotInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['client', 'service', 'staff', 'start_datetime', 'status']
    list_filter = ['status', 'business']
    search_fields = ['client__first_name', 'client__last_name', 'client__email']
    date_hierarchy = 'start_datetime'


@admin.register(BookingBlock)
class BookingBlockAdmin(admin.ModelAdmin):
    list_display = ['staff', 'start_datetime', 'end_datetime', 'reason']
    list_filter = ['staff']


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week']
