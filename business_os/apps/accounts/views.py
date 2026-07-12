from __future__ import annotations

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from business_os.apps.accounts.services import (
    PORTAL_SESSION_KEY,
    PortalSessionScope,
    audit_auth_event,
    clear_login_failures,
    clear_portal_session,
    default_redirect_for_portal,
    is_login_rate_limited,
    mark_portal_session,
    portal_scope_for_request,
    record_login_failure,
    safe_portal_redirect,
    user_can_access_portal,
)


def portal_login(
    request: HttpRequest,
    portal_hint: str = "",
) -> HttpResponse:
    portal_scope = portal_scope_for_request(request, portal_hint=portal_hint)
    if portal_scope is None:
        raise Http404("Login is not available on this host.")
    if portal_scope == PortalSessionScope.CUSTOMER:
        raise Http404("Customer accounts are not enabled yet.")

    default_path = default_redirect_for_portal(request.user, portal_scope)
    if request.user.is_authenticated and request.session.get(PORTAL_SESSION_KEY) == portal_scope:
        return redirect(default_path)

    if request.method == "POST":
        username = request.POST.get("username", "")
        if is_login_rate_limited(
            request=request,
            portal_scope=portal_scope,
            username=username,
        ):
            form = AuthenticationForm(request)
            audit_auth_event(
                request=request,
                action="auth.login.rate_limited",
                portal_scope=portal_scope,
                username=username,
                reason="Login rate limit exceeded.",
            )
            return _render_login(
                request,
                form,
                portal_scope,
                status=429,
                error_message="Too many login attempts. Try again later.",
            )

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user_can_access_portal(user, portal_scope):
                form.add_error(None, "This account is not allowed to access this portal.")
                audit_auth_event(
                    request=request,
                    action="auth.login.denied",
                    portal_scope=portal_scope,
                    username=username,
                    actor=user,
                    reason="Authenticated user does not have portal access.",
                )
                return _render_login(request, form, portal_scope, status=403)

            login(request, user)
            mark_portal_session(request, portal_scope)
            clear_login_failures(
                request=request,
                portal_scope=portal_scope,
                username=username,
            )
            audit_auth_event(
                request=request,
                action="auth.login.succeeded",
                portal_scope=portal_scope,
                username=username,
                actor=user,
            )
            default_path = default_redirect_for_portal(user, portal_scope)
            return redirect(
                safe_portal_redirect(
                    request,
                    portal_scope=portal_scope,
                    default_path=default_path,
                )
            )
        record_login_failure(
            request=request,
            portal_scope=portal_scope,
            username=username,
        )
        audit_auth_event(
            request=request,
            action="auth.login.failed",
            portal_scope=portal_scope,
            username=username,
            reason="Invalid credentials or inactive account.",
        )
    elif request.method == "GET":
        form = AuthenticationForm(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    return _render_login(request, form, portal_scope)


def portal_logout(
    request: HttpRequest,
    portal_hint: str = "",
) -> HttpResponse:
    portal_scope = portal_scope_for_request(request, portal_hint=portal_hint)
    if portal_scope is None:
        raise Http404("Logout is not available on this host.")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    audit_auth_event(
        request=request,
        action="auth.logout.succeeded",
        portal_scope=portal_scope,
        actor=request.user if request.user.is_authenticated else None,
    )
    clear_portal_session(request)
    logout(request)
    return redirect("/login/" if portal_scope != PortalSessionScope.CUSTOMER else "/")


def _render_login(
    request: HttpRequest,
    form: AuthenticationForm,
    portal_scope: str,
    *,
    status: int = 200,
    error_message: str = "",
) -> HttpResponse:
    portal_name = {
        PortalSessionScope.BUSINESS_ADMIN: "Business Admin",
        PortalSessionScope.PLATFORM_ADMIN: "Platform",
    }.get(portal_scope, "Business OS")
    return render(
        request,
        "accounts/portal_login.html",
        {
            "form": form,
            "portal_name": portal_name,
            "portal_scope": portal_scope,
            "next": request.GET.get("next", ""),
            "error_message": error_message,
        },
        status=status,
    )
