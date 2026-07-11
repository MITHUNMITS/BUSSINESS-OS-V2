from django.contrib import admin
from django.urls import include, path

from business_os.api.router import api
from business_os.apps.core.views import health_database, health_live, health_ready, root
from business_os.portals import views as portal_views

urlpatterns = [
    path("", root, name="root"),
    path("health/live", health_live, name="health-live"),
    path("health/ready", health_ready, name="health-ready"),
    path("health/database", health_database, name="health-database"),
    path("django-admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("app/", include("business_os.portals.admin_urls")),
    path("platform/", include("business_os.portals.platform_urls")),
    path("modules/", portal_views.platform_modules, name="platform-modules-canonical"),
    path(
        "organizations/",
        portal_views.platform_organizations,
        name="platform-organizations-canonical",
    ),
    path("", include("business_os.portals.admin_urls")),
    path("", include("business_os.apps.websites.urls")),
]
