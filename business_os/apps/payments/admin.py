from django.contrib import admin

from business_os.apps.payments.models import PaymentIntent, PaymentProvider, PaymentTransaction

admin.site.register(PaymentProvider)
admin.site.register(PaymentIntent)
admin.site.register(PaymentTransaction)

