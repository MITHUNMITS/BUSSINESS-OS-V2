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
        if host_resolution.website is not None:
            request.organization = host_resolution.website.organization

        if not is_path_allowed_for_surface(
            surface=host_resolution.surface,
            path=request.path,
        ):
            raise Http404("This route is not exposed on this host.")

        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        response["X-BusinessOS-Surface"] = host_resolution.surface
        return response
