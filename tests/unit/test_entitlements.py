from datetime import timedelta

from django.utils import timezone

from business_os.apps.entitlements.models import EntitlementState, OrganizationEntitlement
from business_os.apps.entitlements.services import grant_entitlement, has_entitlement
from business_os.apps.organizations.models import Organization


def test_granted_entitlement_is_active(db):
    organization = Organization.objects.create(slug="acme", name="Acme", default_currency="AED")

    grant_entitlement(organization=organization, code="commerce.checkout", source="test")

    assert has_entitlement(organization=organization, capability_code="commerce.checkout")


def test_expired_entitlement_is_not_active(db):
    organization = Organization.objects.create(slug="acme", name="Acme", default_currency="AED")
    OrganizationEntitlement.objects.create(
        organization=organization,
        code="commerce.checkout",
        state=EntitlementState.ACTIVE,
        ends_at=timezone.now() - timedelta(days=1),
    )

    assert not has_entitlement(organization=organization, capability_code="commerce.checkout")
