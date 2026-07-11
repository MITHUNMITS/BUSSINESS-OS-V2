from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from business_os.apps.entitlements.services import grant_entitlement
from business_os.apps.marketplace.models import Capability, Module
from business_os.apps.subscriptions.models import (
    OrganizationSubscription,
    SubscriptionItem,
    SubscriptionStatus,
)


@transaction.atomic
def activate_subscription(
    *,
    organization,
    modules: Iterable[Module],
    capabilities: Iterable[Capability],
    currency: str,
    billing_period: str = "monthly",
) -> OrganizationSubscription:
    subscription = OrganizationSubscription.objects.create(
        organization=organization,
        currency=currency,
        billing_period=billing_period,
        status=SubscriptionStatus.ACTIVE,
        starts_at=timezone.now(),
        renews_at=timezone.now() + timedelta(days=30 if billing_period == "monthly" else 365),
    )

    module_list = list(modules)
    capability_list = list(capabilities)
    for module in module_list:
        SubscriptionItem.objects.create(
            organization=organization,
            subscription=subscription,
            module=module,
            quantity=1,
            unit_price=Decimal("0.00"),
            price_snapshot={"source": "manual-or-free"},
        )
        grant_entitlement(organization=organization, code=f"{module.code}.enabled", source="subscription")

    for capability in capability_list:
        module = module_list[0] if module_list else None
        if module is None:
            continue
        SubscriptionItem.objects.create(
            organization=organization,
            subscription=subscription,
            module=module,
            capability=capability,
            quantity=1,
            unit_price=Decimal("0.00"),
            price_snapshot={"source": "manual-or-free"},
        )
        grant_entitlement(organization=organization, code=capability.code, source="subscription")

    return subscription
