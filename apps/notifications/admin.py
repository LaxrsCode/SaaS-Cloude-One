from django.contrib import admin

from .models import EmailReminder, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    search_fields = ['title', 'message', 'user__email']
    date_hierarchy = 'created_at'


@admin.register(EmailReminder)
class EmailReminderAdmin(admin.ModelAdmin):
    list_display = ['booking', 'type', 'recipient_email', 'status', 'sent_at']
    list_filter = ['type', 'status']
    search_fields = ['recipient_email']
