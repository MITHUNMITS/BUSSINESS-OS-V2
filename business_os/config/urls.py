from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy

from business_os.api.router import api
from business_os.apps.accounts import views as account_views
from business_os.apps.accounts.services import PortalSessionScope
from business_os.apps.core.views import health_database, health_live, health_ready, root
from business_os.portals import views as portal_views

urlpatterns = [
    path("", root, name="root"),
    path("health/live", health_live, name="health-live"),
    path("health/ready", health_ready, name="health-ready"),
    path("health/database", health_database, name="health-database"),
    path("django-admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("login/", account_views.portal_login, name="portal-login"),
    path("logout/", account_views.portal_logout, name="portal-logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password-reset-done"),
            template_name="registration/password_reset_form.html",
        ),
        name="password-reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password-reset-done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("password-reset-complete"),
            template_name="registration/password_reset_confirm.html",
        ),
        name="password-reset-confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password-reset-complete",
    ),
    path(
        "app/login/",
        account_views.portal_login,
        {"portal_hint": PortalSessionScope.BUSINESS_ADMIN},
        name="business-portal-login",
    ),
    path(
        "app/logout/",
        account_views.portal_logout,
        {"portal_hint": PortalSessionScope.BUSINESS_ADMIN},
        name="business-portal-logout",
    ),
    path(
        "platform/login/",
        account_views.portal_login,
        {"portal_hint": PortalSessionScope.PLATFORM_ADMIN},
        name="platform-portal-login",
    ),
    path(
        "platform/logout/",
        account_views.portal_logout,
        {"portal_hint": PortalSessionScope.PLATFORM_ADMIN},
        name="platform-portal-logout",
    ),
    path("app/", include("business_os.portals.admin_urls")),
    path("platform/", include("business_os.portals.platform_urls")),
    path("modules/", portal_views.platform_modules, name="platform-modules-canonical"),
    path(
        "organizations/",
        portal_views.platform_organizations,
        name="platform-organizations-canonical",
    ),
    path(
        "organizations/<slug:organization_slug>/support/start/",
        portal_views.platform_start_support_session,
        name="platform-support-start-canonical",
    ),
    path(
        "organizations/<slug:organization_slug>/support/end/",
        portal_views.platform_end_support_session,
        name="platform-support-end-canonical",
    ),
    path(
        "organizations/<slug:organization_slug>/",
        portal_views.platform_organization_workspace,
        name="platform-organization-workspace-canonical",
    ),
    path("", include("business_os.portals.admin_urls")),
    path("", include("business_os.apps.websites.urls")),
]
