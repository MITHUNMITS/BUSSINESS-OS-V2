from django.contrib import admin

from business_os.apps.entitlements.models import OrganizationEntitlement, UsageLimit

admin.site.register(OrganizationEntitlement)
admin.site.register(UsageLimit)

