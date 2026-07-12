from __future__ import annotations

import hashlib
from typing import Any

from django.conf import settings
from django.contrib.auth import logout
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme

from business_os.apps.core.models import PlatformPermission
from business_os.apps.core.services import AuditTarget, audit_event, has_platform_permission
from business_os.apps.organizations.models import Membership

PORTAL_SESSION_KEY = "business_os.portal_scope"
LOGIN_RATE_LIMIT_PREFIX = "business_os.login_failures"


class PortalSessionScope:
    BUSINESS_ADMIN = "business_admin"
    PLATFORM_ADMIN = "platform_admin"
    CUSTOMER = "customer"


PUBLIC_SITE_SURFACES = {"generated_site", "custom_site", "preview"}
PORTAL_LOGIN_PATHS = {
    "/login/",
    "/logout/",
    "/password-reset/",
    "/app/login/",
    "/app/logout/",
    "/platform/login/",
    "/platform/logout/",
    "/account/login/",
    "/account/logout/",
}
PORTAL_DEFAULT_PATHS = {
    PortalSessionScope.BUSINESS_ADMIN: "/",
    PortalSessionScope.PLATFORM_ADMIN: "/organizations/",
    PortalSessionScope.CUSTOMER: "/account/",
}
PORTAL_ALLOWED_REDIRECT_PREFIXES = {
    PortalSessionScope.BUSINESS_ADMIN: ("/o/", "/login/", "/logout/"),
    PortalSessionScope.PLATFORM_ADMIN: (
        "/",
        "/modules/",
        "/organizations/",
        "/login/",
        "/logout/",
    ),
    PortalSessionScope.CUSTOMER: (
        "/",
        "/account/",
        "/p/",
        "/products/",
        "/collections/",
        "/categories/",
        "/cart/",
        "/checkout/",
        "/orders/",
    ),
}


def portal_scope_for_request(request: HttpRequest, *, portal_hint: str = "") -> str | None:
    if portal_hint in {
        PortalSessionScope.BUSINESS_ADMIN,
        PortalSessionScope.PLATFORM_ADMIN,
        PortalSessionScope.CUSTOMER,
    }:
        return portal_hint

    path = request.path
    surface = getattr(request, "host_surface", "")
    if surface == "platform_admin" or path.startswith("/platform/"):
        return PortalSessionScope.PLATFORM_ADMIN
    if surface == "business_admin" or path.startswith("/app/") or path.startswith("/o/"):
        return PortalSessionScope.BUSINESS_ADMIN
    if surface in PUBLIC_SITE_SURFACES or path.startswith("/account/"):
        return PortalSessionScope.CUSTOMER
    return None


def mark_portal_session(request: HttpRequest, portal_scope: str) -> None:
    request.session[PORTAL_SESSION_KEY] = portal_scope
    request.portal_scope = portal_scope


def clear_portal_session(request: HttpRequest) -> None:
    if hasattr(request, "session"):
        request.session.pop(PORTAL_SESSION_KEY, None)
    request.portal_scope = None


def enforce_portal_session_boundary(request: HttpRequest) -> None:
    request.portal_scope = (
        request.session.get(PORTAL_SESSION_KEY) if hasattr(request, "session") else None
    )

    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return

    expected_scope = portal_scope_for_request(request)
    if expected_scope is None:
        return

    if request.portal_scope == expected_scope:
        return

    audit_auth_event(
        request=request,
        action="auth.session.rejected",
        portal_scope=expected_scope,
        actor=user,
        reason="Portal session scope mismatch.",
        after={
            "expected_portal_scope": expected_scope,
            "actual_portal_scope": request.portal_scope,
            "surface": getattr(request, "host_surface", ""),
        },
    )
    logout(request)
    request.portal_scope = None

    if request.path in PORTAL_LOGIN_PATHS or request.path.startswith("/password-reset/"):
        return
    if expected_scope == PortalSessionScope.CUSTOMER:
        return
    raise PermissionDenied("This session is not valid for this portal.")


def user_can_access_portal(user: Any, portal_scope: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if portal_scope == PortalSessionScope.PLATFORM_ADMIN:
        return has_platform_permission(user, PlatformPermission.PORTAL_ACCESS)
    if portal_scope == PortalSessionScope.BUSINESS_ADMIN:
        return Membership.objects.filter(
            user=user,
            membership_status="active",
        ).exists()
    if portal_scope == PortalSessionScope.CUSTOMER:
        return False
    return False


def default_redirect_for_portal(user: Any, portal_scope: str) -> str:
    if portal_scope == PortalSessionScope.BUSINESS_ADMIN and getattr(
        user,
        "is_authenticated",
        False,
    ):
        membership = (
            Membership.objects.select_related("organization")
            .filter(user=user, membership_status="active")
            .order_by("organization__name")
            .first()
        )
        if membership is not None:
            return f"/o/{membership.organization.slug}/dashboard/"
    return PORTAL_DEFAULT_PATHS.get(portal_scope, "/")


def safe_portal_redirect(
    request: HttpRequest,
    *,
    portal_scope: str,
    default_path: str,
) -> str:
    candidate = request.POST.get("next") or request.GET.get("next") or ""
    if not candidate:
        return default_path

    if not url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return default_path

    allowed_prefixes = PORTAL_ALLOWED_REDIRECT_PREFIXES.get(portal_scope, ("/",))
    if candidate.startswith(allowed_prefixes):
        return candidate
    return default_path


def is_login_rate_limited(
    *,
    request: HttpRequest,
    portal_scope: str,
    username: str,
) -> bool:
    return _login_failure_count(
        request=request,
        portal_scope=portal_scope,
        username=username,
    ) >= settings.AUTH_LOGIN_FAILURE_LIMIT


def record_login_failure(
    *,
    request: HttpRequest,
    portal_scope: str,
    username: str,
) -> int:
    key = _login_rate_limit_key(
        request=request,
        portal_scope=portal_scope,
        username=username,
    )
    timeout = settings.AUTH_LOGIN_FAILURE_WINDOW_SECONDS
    cache.add(key, 0, timeout=timeout)
    try:
        attempts = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=timeout)
        attempts = 1
    return attempts


def clear_login_failures(
    *,
    request: HttpRequest,
    portal_scope: str,
    username: str,
) -> None:
    cache.delete(
        _login_rate_limit_key(
            request=request,
            portal_scope=portal_scope,
            username=username,
        )
    )


def audit_auth_event(
    *,
    request: HttpRequest,
    action: str,
    portal_scope: str,
    username: str = "",
    actor: Any | None = None,
    reason: str = "",
    after: dict[str, Any] | None = None,
) -> None:
    payload = {
        "portal_scope": portal_scope,
        "surface": getattr(request, "host_surface", ""),
    }
    if username:
        payload["username"] = username
    if after:
        payload.update(after)
    audit_event(
        action=action,
        request=request,
        actor=actor,
        target=AuditTarget(
            "user",
            _auth_target_id(actor=actor, username=username),
        ),
        after=payload,
        reason=reason,
        source="auth",
    )


def _login_failure_count(
    *,
    request: HttpRequest,
    portal_scope: str,
    username: str,
) -> int:
    return int(
        cache.get(
            _login_rate_limit_key(
                request=request,
                portal_scope=portal_scope,
                username=username,
            ),
            0,
        )
        or 0
    )


def _login_rate_limit_key(
    *,
    request: HttpRequest,
    portal_scope: str,
    username: str,
) -> str:
    identity = username.strip().lower()
    ip_address = request.META.get("REMOTE_ADDR", "unknown")
    digest = hashlib.sha256(
        f"{portal_scope}:{identity}:{ip_address}".encode()
    ).hexdigest()
    return f"{LOGIN_RATE_LIMIT_PREFIX}:{digest}"


def _auth_target_id(*, actor: Any | None, username: str) -> str:
    actor_id = getattr(actor, "id", None)
    if actor_id:
        return str(actor_id)
    if username:
        return hashlib.sha256(username.strip().lower().encode()).hexdigest()[:32]
    return ""
