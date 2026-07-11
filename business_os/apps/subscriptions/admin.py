from django.contrib import admin

from business_os.apps.subscriptions.models import (
    OrganizationSubscription,
    PlatformBillingInvoice,
    PlatformBillingInvoiceLine,
    PlatformBillingPayment,
    SubscriptionItem,
)

admin.site.register(OrganizationSubscription)
admin.site.register(SubscriptionItem)
admin.site.register(PlatformBillingInvoice)
admin.site.register(PlatformBillingInvoiceLine)
admin.site.register(PlatformBillingPayment)
