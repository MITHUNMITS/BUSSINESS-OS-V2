from __future__ import annotations

import uuid
from collections.abc import Callable

from django.http import Http404, HttpRequest, HttpResponse


class RequestContextMiddleware:
    """Attach stable request metadata used by audit, logs, and service calls."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        from business_os.apps.websites.domain_services import (
            is_path_allowed_for_surface,
            resolve_host,
        )

        host_resolution = resolve_host(request.get_host())
        request.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.organization = None
        request.facility = None
        request.host_surface = host_resolution.surface
        request.website = host_resolution.website
        request.locale = getattr(request, "LANGUAGE_CODE", "en")
        request.currency = None
        request.support_session = None
        if host_resolution.website is not None:
            request.organization = host_resolution.website.organization

        if not is_path_allowed_for_surface(
            surface=host_resolution.surface,
            path=request.path,
        ):
            raise Http404("This route is not exposed on this host.")

        self._enforce_portal_session_boundary(request)
        self._attach_support_session(request)
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        response["X-BusinessOS-Surface"] = host_resolution.surface
        return response

    def _enforce_portal_session_boundary(self, request: HttpRequest) -> None:
        if not hasattr(request, "session"):
            return

        from business_os.apps.accounts.services import enforce_portal_session_boundary

        enforce_portal_session_boundary(request)

    def _attach_support_session(self, request: HttpRequest) -> None:
        if not getattr(getattr(request, "user", None), "is_authenticated", False):
            return
        if not hasattr(request, "session"):
            return

        from business_os.apps.core.services import (
            SUPPORT_SESSION_KEY,
            get_active_support_session,
        )

        session_id = request.session.get(SUPPORT_SESSION_KEY)
        support_session = get_active_support_session(
            actor=request.user,
            session_id=session_id,
        )
        if support_session is None:
            request.session.pop(SUPPORT_SESSION_KEY, None)
            return
        request.support_session = support_session
