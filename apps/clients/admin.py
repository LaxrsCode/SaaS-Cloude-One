from django.contrib import admin

from .models import Client, ClientNote


class ClientNoteInline(admin.TabularInline):
    model = ClientNote
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'business', 'total_visits', 'last_visit')
    list_filter = ('business',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    inlines = [ClientNoteInline]