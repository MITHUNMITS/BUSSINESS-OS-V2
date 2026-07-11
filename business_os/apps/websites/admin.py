from django.contrib import admin

from business_os.apps.websites.models import Website, WebsitePage, WebsiteSection, WebsiteTheme, WebsiteVersion

admin.site.register(Website)
admin.site.register(WebsiteTheme)
admin.site.register(WebsitePage)
admin.site.register(WebsiteSection)
admin.site.register(WebsiteVersion)

