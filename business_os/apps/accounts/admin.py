from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from business_os.apps.accounts.models import User


@admin.register(User)
class BusinessOSUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_platform_staff", "is_active")
    list_filter = ("is_staff", "is_platform_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Business OS", {"fields": ("phone_number", "locale", "timezone", "is_platform_staff")}),
    )
