from django.contrib import admin

from business_os.apps.websites.models import (
    Website,
    WebsiteDomain,
    WebsitePage,
    WebsiteSection,
    WebsiteTheme,
    WebsiteVersion,
)

admin.site.register(Website)
admin.site.register(WebsiteDomain)
admin.site.register(WebsiteTheme)
admin.site.register(WebsitePage)
admin.site.register(WebsiteSection)
admin.site.register(WebsiteVersion)
