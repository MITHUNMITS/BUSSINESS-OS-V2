from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, override_settings
from django.utils import timezone

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.core.models import (
    AuditEvent,
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    SupportAccessScope,
    SupportSession,
)
from business_os.apps.core.services import (
    SUPPORT_SESSION_KEY,
    end_support_session,
    require_support_access,
    start_support_session,
)
from business_os.apps.organizations.models import Membership, Organization

HOST_SETTINGS = {
    "PLATFORM_ROOT_DOMAIN": "businessos.local",
    "ALLOWED_HOSTS": [".businessos.local"],
}


def create_user(username: str, *, is_platform_staff: bool = False):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="not-used",
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


def support_agent():
    user = create_user("support-agent", is_platform_staff=True)
    assign_platform_role(
        user,
        [
            PlatformPermission.PORTAL_ACCESS,
            PlatformPermission.SUPPORT_SESSION_START,
            PlatformPermission.SUPPORT_SESSION_READ,
        ],
    )
    return user


def force_portal_login(client: Client, user, portal_scope: str) -> None:
    client.force_login(user)
    session = client.session
    session[PORTAL_SESSION_KEY] = portal_scope
    session.save()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_can_access_only_own_org_admin():
    user = create_user("business-owner")
    own_organization = create_organization("nova")
    other_organization = create_organization("atlas")
    Membership.objects.create(
        organization=own_organization,
        user=user,
        is_owner=True,
    )
    client = Client(HTTP_HOST="app.businessos.local")
    force_portal_login(client, user, PortalSessionScope.BUSINESS_ADMIN)

    own_response = client.get(f"/o/{own_organization.slug}/dashboard/")
    other_response = client.get(f"/o/{other_organization.slug}/dashboard/")

    assert own_response.status_code == 200
    assert other_response.status_code == 403


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_platform_staff_with_platform_role_can_access_platform_portal():
    user = create_user("platform-operator", is_platform_staff=True)
    assign_platform_role(user, [PlatformPermission.PORTAL_ACCESS])
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, user, PortalSessionScope.PLATFORM_ADMIN)

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-BusinessOS-Surface"] == "platform_admin"


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_non_platform_user_cannot_access_platform_portal():
    user = create_user("not-platform")
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, user, PortalSessionScope.PLATFORM_ADMIN)

    response = client.get("/")

    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_platform_staff_without_role_cannot_access_platform_portal():
    user = create_user("staff-without-role", is_platform_staff=True)
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, user, PortalSessionScope.PLATFORM_ADMIN)

    response = client.get("/")

    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_support_session_grants_only_scoped_platform_workspace_access():
    agent = support_agent()
    target_organization = create_organization("nova")
    other_organization = create_organization("atlas")
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, agent, PortalSessionScope.PLATFORM_ADMIN)

    start_response = client.post(
        f"/organizations/{target_organization.slug}/support/start/",
        {
            "reason": "Investigating support ticket SUP-42",
            "ticket_reference": "SUP-42",
            "duration_minutes": "60",
        },
    )
    support_session = SupportSession.objects.get(
        actor=agent,
        organization=target_organization,
    )
    workspace_response = client.get(f"/organizations/{target_organization.slug}/")
    other_response = client.get(f"/organizations/{other_organization.slug}/")

    business_client = Client(HTTP_HOST="app.businessos.local")
    force_portal_login(business_client, agent, PortalSessionScope.BUSINESS_ADMIN)
    browser_session = business_client.session
    browser_session[SUPPORT_SESSION_KEY] = str(support_session.id)
    browser_session.save()
    business_response = business_client.get(f"/o/{target_organization.slug}/dashboard/")

    assert start_response.status_code == 302
    assert workspace_response.status_code == 200
    assert b"Support mode active" in workspace_response.content
    assert other_response.status_code == 403
    assert business_response.status_code == 403
    assert not Membership.objects.filter(
        organization=target_organization,
        user=agent,
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_expired_support_session_fails():
    agent = support_agent()
    organization = create_organization("nova")
    support_session = start_support_session(
        actor=agent,
        organization=organization,
        reason="Checking a stale support session",
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    now = timezone.now()
    SupportSession.objects.filter(id=support_session.id).update(
        started_at=now - timedelta(hours=2),
        expires_at=now - timedelta(hours=1),
    )
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, agent, PortalSessionScope.PLATFORM_ADMIN)
    browser_session = client.session
    browser_session[SUPPORT_SESSION_KEY] = str(support_session.id)
    browser_session.save()

    response = client.get(f"/organizations/{organization.slug}/")

    assert response.status_code == 403
    assert SUPPORT_SESSION_KEY not in client.session


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_support_access_writes_audit_event():
    agent = support_agent()
    organization = create_organization("nova")
    client = Client(HTTP_HOST="platform.businessos.local")
    force_portal_login(client, agent, PortalSessionScope.PLATFORM_ADMIN)

    client.post(
        f"/organizations/{organization.slug}/support/start/",
        {
            "reason": "Investigating support ticket SUP-99",
            "ticket_reference": "SUP-99",
            "duration_minutes": "60",
        },
    )
    support_session = SupportSession.objects.get(actor=agent, organization=organization)
    client.get(f"/organizations/{organization.slug}/")

    started_event = AuditEvent.objects.get(action="support.session.started")
    accessed_event = AuditEvent.objects.get(action="support.session.accessed")

    assert started_event.support_mode is True
    assert started_event.support_session == support_session
    assert started_event.actor == agent
    assert started_event.organization == organization
    assert started_event.reason == "Investigating support ticket SUP-99"
    assert accessed_event.support_mode is True
    assert accessed_event.support_session == support_session


@pytest.mark.django_db
def test_end_support_session_closes_session_and_writes_audit_event():
    agent = support_agent()
    organization = create_organization("nova")
    support_session = start_support_session(
        actor=agent,
        organization=organization,
        reason="Done with support review",
        expires_at=timezone.now() + timedelta(minutes=30),
    )

    with pytest.raises(PermissionDenied):
        require_support_access(
            support_session=support_session,
            organization=organization,
            action="edit",
        )
    ended_session = end_support_session(actor=agent, support_session=support_session)

    assert support_session.scope == SupportAccessScope.READ_ONLY
    assert ended_session.ended_at is not None
    assert ended_session.ended_by == agent
    assert AuditEvent.objects.filter(
        action="support.session.ended",
        support_session=support_session,
        support_mode=True,
    ).exists()
