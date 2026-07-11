from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from business_os.apps.core.services import AuditTarget, audit_event
from business_os.apps.organizations.models import Facility, Membership, Organization


@dataclass(frozen=True)
class OrganizationOnboardingResult:
    organization: Organization
    facility: Facility
    owner_membership: Membership


@transaction.atomic
def onboard_organization(
    *,
    owner_email: str,
    owner_username: str,
    organization_name: str,
    country: str = "AE",
    currency: str = "AED",
    timezone: str = "Asia/Dubai",
) -> OrganizationOnboardingResult:
    user_model = get_user_model()
    owner, _created = user_model.objects.get_or_create(
        username=owner_username,
        defaults={"email": owner_email, "timezone": timezone},
    )
    organization = Organization.objects.create(
        slug=slugify(organization_name),
        name=organization_name,
        country=country,
        default_currency=currency,
        timezone=timezone,
    )
    facility = Facility.objects.create(
        organization=organization,
        name="Online Store",
        code="online",
        facility_type=Facility.FacilityType.ONLINE,
        timezone=timezone,
        currency=currency,
        languages=["en"],
    )
    membership = Membership.objects.create(
        organization=organization,
        facility=facility,
        user=owner,
        is_owner=True,
    )
    audit_event(
        action="organization.onboarded",
        organization=organization,
        facility=facility,
        actor=owner,
        target=AuditTarget("organization", str(organization.id)),
    )
    return OrganizationOnboardingResult(organization, facility, membership)

