from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.utils import timezone

from business_os.apps.entitlements.models import (
    ACTIVE_ENTITLEMENT_STATES,
    EntitlementState,
    OrganizationEntitlement,
    UsageLimit,
)


def has_entitlement(*, organization: Any, capability_code: str, facility: Any | None = None) -> bool:
    organization_id = getattr(organization, "id", organization)
    facility_id = getattr(facility, "id", facility) if facility is not None else None
    now = timezone.now()
    queryset = OrganizationEntitlement.objects.filter(
        organization_id=organization_id,
        code=capability_code,
        state__in=ACTIVE_ENTITLEMENT_STATES,
    ).filter(models_q_current(now))
    if facility_id is not None:
        queryset = queryset.filter(facility_id__in=[facility_id, None])
    return queryset.exists()


def has_any_entitlement(*, organization: Any, capability_codes: Iterable[str]) -> bool:
    organization_id = getattr(organization, "id", organization)
    now = timezone.now()
    return OrganizationEntitlement.objects.filter(
        organization_id=organization_id,
        code__in=list(capability_codes),
        state__in=ACTIVE_ENTITLEMENT_STATES,
    ).filter(models_q_current(now)).exists()


def models_q_current(now):
    from django.db.models import Q

    return Q(ends_at__isnull=True) | Q(ends_at__gt=now)


@transaction.atomic
def grant_entitlement(
    *,
    organization: Any,
    code: str,
    facility: Any | None = None,
    state: str = EntitlementState.ACTIVE,
    source: str = "manual",
    limits: dict | None = None,
) -> OrganizationEntitlement:
    entitlement, _created = OrganizationEntitlement.objects.update_or_create(
        organization=organization,
        facility=facility,
        code=code,
        defaults={
            "state": state,
            "source": source,
            "starts_at": timezone.now(),
            "ends_at": None,
            "limits": limits or {},
        },
    )
    return entitlement


@transaction.atomic
def initialize_limit(
    *,
    organization: Any,
    code: str,
    included_quantity,
    unit: str,
    facility: Any | None = None,
) -> UsageLimit:
    limit, _created = UsageLimit.objects.update_or_create(
        organization=organization,
        facility=facility,
        code=code,
        defaults={"included_quantity": included_quantity, "unit": unit},
    )
    return limit

