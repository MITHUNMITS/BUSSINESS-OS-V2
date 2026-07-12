from django.urls import path

from business_os.portals import views

urlpatterns = [
    path("", views.platform_overview, name="platform-overview"),
    path("modules/", views.platform_modules, name="platform-modules"),
    path("organizations/", views.platform_organizations, name="platform-organizations"),
    path(
        "organizations/<slug:organization_slug>/support/start/",
        views.platform_start_support_session,
        name="platform-support-start",
    ),
    path(
        "organizations/<slug:organization_slug>/support/end/",
        views.platform_end_support_session,
        name="platform-support-end",
    ),
    path(
        "organizations/<slug:organization_slug>/",
        views.platform_organization_workspace,
        name="platform-organization-workspace",
    ),
]
