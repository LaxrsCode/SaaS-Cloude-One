from django.contrib import admin

from .models import Business, BusinessMember, BusinessSettings


class BusinessSettingsInline(admin.StackedInline):
    model = BusinessSettings


class BusinessMemberInline(admin.TabularInline):
    model = BusinessMember
    extra = 1


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'owner', 'subscription_tier', 'is_active']
    list_filter = ['category', 'subscription_tier', 'is_active']
    search_fields = ['name', 'slug', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BusinessSettingsInline, BusinessMemberInline]


@admin.register(BusinessMember)
class BusinessMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'business', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__email', 'business__name']
