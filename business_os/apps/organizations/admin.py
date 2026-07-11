from django.contrib import admin

from business_os.apps.organizations.models import (
    Facility,
    Membership,
    MembershipRole,
    Organization,
    PermissionGrant,
    Role,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "country", "default_currency", "status")
    search_fields = ("name", "slug", "legal_name")
    list_filter = ("country", "status")


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "facility_type", "currency", "status")
    list_filter = ("facility_type", "status")
    search_fields = ("name", "code", "organization__name")


admin.site.register(Membership)
admin.site.register(Role)
admin.site.register(MembershipRole)
admin.site.register(PermissionGrant)

