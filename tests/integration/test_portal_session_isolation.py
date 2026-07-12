import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.core.models import (
    AuditEvent,
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
)
from business_os.apps.organizations.models import Membership, Organization
from business_os.apps.websites.services import provision_default_website

HOST_SETTINGS = {
    "PLATFORM_ROOT_DOMAIN": "businessos.local",
    "ALLOWED_HOSTS": [".businessos.local"],
}


def create_user(username: str, *, password: str = "secret-pass", is_platform_staff: bool = False):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password,
        is_platform_staff=is_platform_staff,
    )


def create_organization(slug: str) -> Organization:
    return Organization.objects.create(
        slug=slug,
        name=slug.title(),
        default_currency="AED",
    )


def assign_platform_role(user, permissions: list[str]) -> None:
    role, _created = PlatformRole.objects.get_or_create(
        code=f"test-platform-{user.username}",
        defaults={
            "name": f"Test platform role for {user.username}",
            "permissions": permissions,
            "is_system": True,
        },
    )
    role.permissions = permissions
    role.save(update_fields=["permissions"])
    PlatformRoleAssignment.objects.create(user=user, role=role)


def force_portal_session(client: Client, user, portal_scope: str) -> None:
    client.force_login(user)
    session = client.session
    session[PORTAL_SESSION_KEY] = portal_scope
    session.save()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_login_marks_business_admin_session_and_redirects_to_org_dashboard():
    user = create_user("business-owner")
    organization = create_organization("nova")
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")

    response = client.post(
        "/login/",
        {"username": user.username, "password": "secret-pass"},
    )

    assert response.status_code == 302
    assert response.url == f"/o/{organization.slug}/dashboard/"
    assert client.session[PORTAL_SESSION_KEY] == PortalSessionScope.BUSINESS_ADMIN
    assert AuditEvent.objects.filter(
        action="auth.login.succeeded",
        actor=user,
        source="auth",
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_platform_login_marks_platform_session_and_rejects_external_next_url():
    user = create_user("platform-admin", is_platform_staff=True)
    assign_platform_role(user, [PlatformPermission.PORTAL_ACCESS])
    client = Client(HTTP_HOST="platform.businessos.local")

    response = client.post(
        "/login/?next=https://evil.example/phish",
        {"username": user.username, "password": "secret-pass"},
    )

    assert response.status_code == 302
    assert response.url == "/organizations/"
    assert client.session[PORTAL_SESSION_KEY] == PortalSessionScope.PLATFORM_ADMIN


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_session_cannot_be_reused_on_platform_host():
    user = create_user("business-owner")
    organization = create_organization("nova")
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_portal_session(client, user, PortalSessionScope.BUSINESS_ADMIN)

    response = client.get("/organizations/", HTTP_HOST="platform.businessos.local")

    assert response.status_code == 403
    assert PORTAL_SESSION_KEY not in client.session
    assert AuditEvent.objects.filter(
        action="auth.session.rejected",
        actor=user,
        source="auth",
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_platform_session_cannot_be_reused_on_business_admin_host():
    user = create_user("platform-admin", is_platform_staff=True)
    assign_platform_role(user, [PlatformPermission.PORTAL_ACCESS])
    organization = create_organization("nova")
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_session(client, user, PortalSessionScope.PLATFORM_ADMIN)

    response = client.get(
        f"/o/{organization.slug}/dashboard/",
        HTTP_HOST="app.businessos.local",
    )

    assert response.status_code == 403
    assert PORTAL_SESSION_KEY not in client.session


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_leaked_privileged_session_is_cleared_on_public_website_host():
    user = create_user("platform-admin", is_platform_staff=True)
    assign_platform_role(user, [PlatformPermission.PORTAL_ACCESS])
    organization = create_organization("nova")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_session(client, user, PortalSessionScope.PLATFORM_ADMIN)

    response = client.get("/", HTTP_HOST="nova.businessos.local")

    assert response.status_code == 200
    assert b"Nova" in response.content
    assert PORTAL_SESSION_KEY not in client.session
    assert AuditEvent.objects.filter(
        action="auth.session.rejected",
        actor=user,
        source="auth",
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS, AUTH_LOGIN_FAILURE_LIMIT=2)
def test_login_failure_is_audited_and_rate_limited():
    client = Client(HTTP_HOST="platform.businessos.local")
    username = f"missing-{uuid.uuid4()}"

    first_response = client.post(
        "/login/",
        {"username": username, "password": "wrong-pass"},
    )
    second_response = client.post(
        "/login/",
        {"username": username, "password": "wrong-pass"},
    )
    limited_response = client.post(
        "/login/",
        {"username": username, "password": "wrong-pass"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert limited_response.status_code == 429
    assert AuditEvent.objects.filter(action="auth.login.failed", source="auth").count() == 2
    assert AuditEvent.objects.filter(action="auth.login.rate_limited", source="auth").count() == 1


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_logout_is_post_only_audited_and_clears_portal_session():
    user = create_user("platform-logout", is_platform_staff=True)
    assign_platform_role(user, [PlatformPermission.PORTAL_ACCESS])
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_session(client, user, PortalSessionScope.PLATFORM_ADMIN)

    get_response = client.get("/logout/")
    post_response = client.post("/logout/")

    assert get_response.status_code == 405
    assert post_response.status_code == 302
    assert post_response.url == "/login/"
    assert PORTAL_SESSION_KEY not in client.session
    assert AuditEvent.objects.filter(
        action="auth.logout.succeeded",
        actor=user,
        source="auth",
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_password_reset_sends_email_without_revealing_account_existence():
    user = create_user("reset-user")
    client = Client(HTTP_HOST="app.businessos.local")

    response = client.post("/password-reset/", {"email": user.email})

    assert response.status_code == 302
    assert response.url == "/password-reset/done/"
    assert len(mail.outbox) == 1
    assert "/password-reset/" in mail.outbox[0].body


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_password_reset_is_not_exposed_on_public_website_host():
    organization = create_organization("nova")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="nova.businessos.local")

    response = client.get("/password-reset/")

    assert response.status_code == 404


def test_session_cookie_is_host_scoped_and_csrf_origins_are_explicit():
    assert settings.SESSION_COOKIE_DOMAIN is None
    assert settings.CSRF_COOKIE_DOMAIN is None
    assert "http://app.businessos.local" in settings.CSRF_TRUSTED_ORIGINS
    assert "https://platform.businessos.local" in settings.CSRF_TRUSTED_ORIGINS
    assert "http://api.localhost" in settings.CSRF_TRUSTED_ORIGINS
