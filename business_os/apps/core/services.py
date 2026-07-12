from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone

from business_os.apps.core.models import (
    AuditEvent,
    PlatformPermission,
    PlatformRoleAssignment,
    SupportAccessScope,
    SupportSession,
)

SUPPORT_SESSION_KEY = "business_os.support_session_id"


@dataclass(frozen=True)
class AuditTarget:
    target_type: str
    target_id: str


def audit_event(
    *,
    action: str,
    request: HttpRequest | None = None,
    organization: Any | None = None,
    facility: Any | None = None,
    actor: Any | None = None,
    target: AuditTarget | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    reason: str = "",
    support_mode: bool = False,
    support_session: SupportSession | None = None,
    source: str = "web",
) -> AuditEvent:
    if request is not None:
        actor = actor or getattr(request, "user", None)
        organization = organization or getattr(request, "organization", None)
        facility = facility or getattr(request, "facility", None)
        support_session = support_session or getattr(request, "support_session", None)
        support_mode = support_mode or support_session is not None

    with transaction.atomic():
        return AuditEvent.objects.create(
            organization=organization,
            facility=facility,
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            support_session=support_session,
            action=action,
            target_type=target.target_type if target else "",
            target_id=target.target_id if target else "",
            before=before or {},
            after=after or {},
            ip_address=_request_ip(request),
            user_agent=_request_user_agent(request),
            request_id=getattr(request, "request_id", "") if request else "",
            reason=reason,
            support_mode=support_mode,
            source=source,
        )


def has_platform_permission(actor: Any, permission: str) -> bool:
    """Return true only for explicit platform role assignments."""

    if not (
        getattr(actor, "is_authenticated", False)
        and getattr(actor, "is_platform_staff", False)
    ):
        return False

    current_time = timezone.now()
    assignments = (
        PlatformRoleAssignment.objects.select_related("role")
        .filter(
            user=actor,
            starts_at__lte=current_time,
            revoked_at__isnull=True,
            role__is_active=True,
        )
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=current_time))
    )

    return any(
        _permission_matches(granted_permission, permission)
        for assignment in assignments
        for granted_permission in assignment.role.permissions
    )


def require_platform_permission(actor: Any, permission: str) -> None:
    if not has_platform_permission(actor, permission):
        raise PermissionDenied(f"Platform permission required: {permission}")


def start_support_session(
    *,
    actor: Any,
    organization: Any,
    reason: str,
    expires_at: Any,
    scope: str = SupportAccessScope.READ_ONLY,
    ticket_reference: str = "",
    request: HttpRequest | None = None,
) -> SupportSession:
    require_platform_permission(actor, PlatformPermission.SUPPORT_SESSION_START)

    reason = reason.strip()
    ticket_reference = ticket_reference.strip()
    if not reason:
        raise ValueError("A support reason is required.")
    if expires_at <= timezone.now():
        raise ValueError("Support sessions must expire in the future.")
    if scope != SupportAccessScope.READ_ONLY:
        raise PermissionDenied(
            "Controlled write support access requires approval controls that are not enabled yet."
        )

    with transaction.atomic():
        support_session = SupportSession.objects.create(
            actor=actor,
            organization=organization,
            reason=reason,
            scope=scope,
            ticket_reference=ticket_reference,
            expires_at=expires_at,
        )
        audit_event(
            action="support.session.started",
            request=request,
            organization=organization,
            actor=actor,
            target=AuditTarget("support_session", str(support_session.id)),
            after={
                "organization_id": str(organization.id),
                "scope": support_session.scope,
                "expires_at": support_session.expires_at.isoformat(),
                "ticket_reference": support_session.ticket_reference,
            },
            reason=support_session.reason,
            support_mode=True,
            support_session=support_session,
            source="platform_support",
        )

    if request is not None and hasattr(request, "session"):
        request.session[SUPPORT_SESSION_KEY] = str(support_session.id)
        request.support_session = support_session

    return support_session


def get_active_support_session(
    *,
    actor: Any,
    session_id: Any,
    organization: Any | None = None,
) -> SupportSession | None:
    if not session_id or not has_platform_permission(
        actor,
        PlatformPermission.SUPPORT_SESSION_READ,
    ):
        return None

    try:
        session_uuid = UUID(str(session_id))
    except (TypeError, ValueError):
        return None

    current_time = timezone.now()
    queryset = SupportSession.objects.select_related("actor", "organization").filter(
        id=session_uuid,
        actor=actor,
        started_at__lte=current_time,
        expires_at__gt=current_time,
        ended_at__isnull=True,
    )
    if organization is not None:
        organization_id = getattr(organization, "id", organization)
        queryset = queryset.filter(organization_id=organization_id)
    return queryset.first()


def require_support_access(
    *,
    support_session: SupportSession | None,
    organization: Any,
    action: str = "view",
) -> SupportSession:
    if support_session is None or not support_session.is_active_at():
        raise PermissionDenied("An active support session is required.")
    if support_session.organization_id != getattr(organization, "id", organization):
        raise PermissionDenied("Support session does not cover this organization.")
    if not support_session.allows_action(action):
        raise PermissionDenied("Support session does not permit this action.")
    return support_session


def end_support_session(
    *,
    actor: Any,
    support_session: SupportSession,
    request: HttpRequest | None = None,
) -> SupportSession:
    if not getattr(actor, "is_authenticated", False):
        raise PermissionDenied("Authenticated platform actor is required.")

    with transaction.atomic():
        current = SupportSession.objects.select_for_update().get(id=support_session.id)
        if current.actor_id != actor.id:
            raise PermissionDenied("Only the support session actor can end this session.")
        if current.ended_at is None:
            current.ended_at = timezone.now()
            current.ended_by = actor
            current.save(update_fields=["ended_at", "ended_by", "updated_at"])
            audit_event(
                action="support.session.ended",
                request=request,
                organization=current.organization,
                actor=actor,
                target=AuditTarget("support_session", str(current.id)),
                after={
                    "organization_id": str(current.organization_id),
                    "ended_at": current.ended_at.isoformat(),
                },
                reason=current.reason,
                support_mode=True,
                support_session=current,
                source="platform_support",
            )

    if request is not None and hasattr(request, "session"):
        if request.session.get(SUPPORT_SESSION_KEY) == str(current.id):
            request.session.pop(SUPPORT_SESSION_KEY, None)
        request.support_session = None

    return current


def record_support_access(
    *,
    request: HttpRequest,
    support_session: SupportSession,
) -> AuditEvent:
    support_session = require_support_access(
        support_session=support_session,
        organization=support_session.organization,
        action="view",
    )
    return audit_event(
        action="support.session.accessed",
        request=request,
        organization=support_session.organization,
        actor=request.user,
        target=AuditTarget("support_session", str(support_session.id)),
        after={
            "organization_id": str(support_session.organization_id),
            "scope": support_session.scope,
        },
        reason=support_session.reason,
        support_mode=True,
        support_session=support_session,
        source="platform_support",
    )


def _permission_matches(granted_permission: Any, required_permission: str) -> bool:
    if not isinstance(granted_permission, str):
        return False
    return (
        granted_permission == PlatformPermission.WILDCARD
        or granted_permission == required_permission
        or (
            granted_permission.endswith(".*")
            and required_permission.startswith(granted_permission[:-1])
        )
    )


def _request_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    return request.META.get("REMOTE_ADDR")


def _request_user_agent(request: HttpRequest | None) -> str:
    if request is None:
        return ""
    return request.headers.get("User-Agent", "")
