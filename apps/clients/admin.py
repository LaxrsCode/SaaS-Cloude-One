from django.contrib import admin

from .models import Client, ClientNote


class ClientNoteInline(admin.TabularInline):
    model = ClientNote
    extra = 0
    readonly_fields = ['author', 'created_at']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'business', 'total_visits']
    list_filter = ['business']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    inlines = [ClientNoteInline]


@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    list_display = ['client', 'author', 'created_at']
    list_filter = ['author']
