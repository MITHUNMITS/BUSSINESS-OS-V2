from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TenantOwnedModel


class EntitlementState(models.TextChoices):
    AVAILABLE = "available", _("Available")
    TRIAL_AVAILABLE = "trial_available", _("Trial available")
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    LIMITED = "limited", _("Limited")
    PAST_DUE = "past_due", _("Past due")
    READ_ONLY = "read_only", _("Read-only")
    SUSPENDED = "suspended", _("Suspended")
    EXPIRED = "expired", _("Expired")
    NOT_PURCHASED = "not_purchased", _("Not purchased")
    NOT_AVAILABLE = "not_available", _("Not available")


ACTIVE_ENTITLEMENT_STATES = {
    EntitlementState.TRIALING,
    EntitlementState.ACTIVE,
    EntitlementState.LIMITED,
}


class OrganizationEntitlement(TenantOwnedModel):
    code = models.SlugField(max_length=120)
    state = models.CharField(
        max_length=32,
        choices=EntitlementState.choices,
        default=EntitlementState.ACTIVE,
        db_index=True,
    )
    source = models.CharField(max_length=80, default="subscription")
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    limits = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "facility", "code"],
                name="unique_entitlement_per_org_facility_code",
                nulls_distinct=False,
            )
        ]
        indexes = [
            models.Index(fields=["organization", "code", "state"]),
            models.Index(fields=["organization", "ends_at"]),
        ]

    def is_current(self) -> bool:
        return self.state in ACTIVE_ENTITLEMENT_STATES and (
            self.ends_at is None or self.ends_at > timezone.now()
        )


class UsageLimit(TenantOwnedModel):
    code = models.SlugField(max_length=120)
    included_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    used_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=40)
    resets_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "facility", "code"],
                name="unique_usage_limit",
                nulls_distinct=False,
            )
        ]

    @property
    def remaining_quantity(self):
        return max(self.included_quantity - self.used_quantity, 0)
