from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import RecordStatus, TenantOwnedModel, TimeStampedModel


class CountryCode(models.TextChoices):
    UAE = "AE", _("United Arab Emirates")
    INDIA = "IN", _("India")


class Organization(TimeStampedModel):
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=180)
    legal_name = models.CharField(max_length=220, blank=True)
    country = models.CharField(max_length=2, choices=CountryCode.choices, default=CountryCode.UAE)
    default_currency = models.CharField(max_length=3, default="AED")
    timezone = models.CharField(max_length=80, default="Asia/Dubai")
    default_locale = models.CharField(max_length=16, default="en")
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE,
        db_index=True,
    )
    tax_registration_number = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug", "status"]),
            models.Index(fields=["country", "status"]),
        ]

    def __str__(self) -> str:
        return self.name


class Facility(TimeStampedModel):
    class FacilityType(models.TextChoices):
        ONLINE = "online", _("Online store")
        RETAIL = "retail", _("Retail store")
        WAREHOUSE = "warehouse", _("Warehouse")
        OFFICE = "office", _("Office")

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="facilities"
    )
    name = models.CharField(max_length=180)
    code = models.SlugField(max_length=80)
    facility_type = models.CharField(
        max_length=40,
        choices=FacilityType.choices,
        default=FacilityType.ONLINE,
    )
    address = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=80, default="Asia/Dubai")
    currency = models.CharField(max_length=3, default="AED")
    languages = models.JSONField(default=list, blank=True)
    operating_hours = models.JSONField(default=dict, blank=True)
    public_visibility = models.BooleanField(default=True)
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_facility_code_per_organization",
            )
        ]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self) -> str:
        return f"{self.organization} / {self.name}"


class Membership(TenantOwnedModel):
    class MembershipStatus(models.TextChoices):
        INVITED = "invited", _("Invited")
        ACTIVE = "active", _("Active")
        SUSPENDED = "suspended", _("Suspended")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    title = models.CharField(max_length=120, blank=True)
    membership_status = models.CharField(
        max_length=32,
        choices=MembershipStatus.choices,
        default=MembershipStatus.ACTIVE,
    )
    is_owner = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_membership_per_organization_user",
            )
        ]
        indexes = [models.Index(fields=["organization", "user", "membership_status"])]

    def __str__(self) -> str:
        return f"{self.user} in {self.organization}"


class Role(TenantOwnedModel):
    code = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"], name="unique_role_code_per_org"
            )
        ]

    def __str__(self) -> str:
        return self.name


class MembershipRole(TenantOwnedModel):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="role_links")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="membership_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "membership", "role"],
                name="unique_membership_role_per_org",
            )
        ]


class PermissionGrant(TenantOwnedModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permission_grants")
    resource = models.CharField(max_length=120)
    action = models.CharField(max_length=80)
    scope = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "role", "resource", "action"],
                name="unique_permission_grant_per_role",
            )
        ]
        indexes = [models.Index(fields=["organization", "resource", "action"])]

    def __str__(self) -> str:
        return f"{self.role}: {self.resource}.{self.action}"
