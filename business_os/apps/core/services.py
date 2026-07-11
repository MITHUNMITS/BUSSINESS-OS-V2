from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.http import HttpRequest

from business_os.apps.core.models import AuditEvent


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
    source: str = "web",
) -> AuditEvent:
    if request is not None:
        actor = actor or getattr(request, "user", None)
        organization = organization or getattr(request, "organization", None)
        facility = facility or getattr(request, "facility", None)

    with transaction.atomic():
        return AuditEvent.objects.create(
            organization=organization,
            facility=facility,
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            action=action,
            target_type=target.target_type if target else "",
            target_id=target.target_id if target else "",
            before=before or {},
            after=after or {},
            request_id=getattr(request, "request_id", "") if request else "",
            reason=reason,
            source=source,
        )
