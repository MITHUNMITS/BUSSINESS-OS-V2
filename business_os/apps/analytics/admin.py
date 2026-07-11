from django.contrib import admin

from business_os.apps.analytics.models import AnalyticsEvent

admin.site.register(AnalyticsEvent)
