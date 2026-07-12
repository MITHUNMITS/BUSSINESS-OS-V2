import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.entitlements.services import grant_entitlement
from business_os.apps.organizations.facility_profiles import resolve_facility_profile
from business_os.apps.organizations.models import Facility, Membership, Organization

HOST_SETTINGS = {
    "PLATFORM_ROOT_DOMAIN": "businessos.local",
    "ALLOWED_HOSTS": [".businessos.local"],
}


def create_user(username: str):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="not-used",
    )


def create_organization(slug: str, *, facility_type: str | None = None) -> Organization:
    organization = Organization.objects.create(
        slug=slug,
        name=slug.title(),
        default_currency="AED",
    )
    if facility_type:
        Facility.objects.create(
            organization=organization,
            name=f"{slug.title()} Facility",
            code="primary",
            facility_type=facility_type,
        )
    return organization


def grant_admin_navigation_entitlements(organization: Organization) -> None:
    for code in ["catalogue.basic", "commerce.orders", "inventory.basic"]:
        grant_entitlement(organization=organization, code=code)


def force_business_portal_login(client: Client, user) -> None:
    client.force_login(user)
    session = client.session
    session[PORTAL_SESSION_KEY] = PortalSessionScope.BUSINESS_ADMIN
    session.save()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("facility_type", "expected_offering", "expected_order", "expected_inventory"),
    [
        (Facility.FacilityType.ONLINE, "Products", "Orders", "Inventory"),
        (Facility.FacilityType.RETAIL, "Products", "Sales", "Stock"),
        (Facility.FacilityType.WAREHOUSE, "Items", "Fulfilment orders", "Stock"),
        (Facility.FacilityType.OFFICE, "Services", "Work requests", "Resources"),
    ],
)
def test_facility_profile_resolves_existing_facility_type_terms(
    facility_type,
    expected_offering,
    expected_order,
    expected_inventory,
):
    organization = create_organization("nova", facility_type=facility_type)

    profile = resolve_facility_profile(organization=organization)

    assert profile.navigation_labels["admin-products"] == expected_offering
    assert profile.navigation_labels["admin-orders"] == expected_order
    assert profile.navigation_labels["admin-inventory"] == expected_inventory


@pytest.mark.django_db
def test_facility_profile_unknown_type_falls_back_to_online_store_terms():
    organization = Organization.objects.create(
        slug="nova",
        name="Nova",
        default_currency="AED",
        metadata={"primary_facility_type": "clinic"},
    )

    profile = resolve_facility_profile(organization=organization)

    assert profile.facility_type == Facility.FacilityType.ONLINE
    assert profile.navigation_labels["admin-products"] == "Products"
    assert profile.dashboard_labels["active_offerings"] == "Active products"


@pytest.mark.django_db
def test_facility_profile_is_organization_scoped_and_does_not_leak_other_org_facility():
    warehouse_organization = create_organization(
        "warehouse-org",
        facility_type=Facility.FacilityType.WAREHOUSE,
    )
    office_organization = create_organization("office-org")
    foreign_facility = warehouse_organization.facilities.get(code="primary")

    office_profile = resolve_facility_profile(organization=office_organization)

    assert office_profile.facility_type == Facility.FacilityType.ONLINE
    assert office_profile.navigation_labels["admin-products"] == "Products"
    with pytest.raises(PermissionDenied):
        resolve_facility_profile(
            organization=office_organization,
            facility=foreign_facility,
        )


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_online_store_admin_dashboard_keeps_ecommerce_terms():
    user = create_user("online-owner")
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    grant_admin_navigation_entitlements(organization)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    response = client.get(f"/o/{organization.slug}/dashboard/")

    assert response.status_code == 200
    assert b"Active products" in response.content
    assert b"Recent orders" in response.content
    assert b"Products" in response.content
    assert b"Orders" in response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_warehouse_admin_dashboard_and_navigation_use_warehouse_terms():
    user = create_user("warehouse-owner")
    organization = create_organization("atlas", facility_type=Facility.FacilityType.WAREHOUSE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    grant_admin_navigation_entitlements(organization)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    response = client.get(f"/o/{organization.slug}/dashboard/")

    assert response.status_code == 200
    assert b"Active items" in response.content
    assert b"Recent fulfilment orders" in response.content
    assert b"Items" in response.content
    assert b"Fulfilment orders" in response.content
    assert b"Stock" in response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_office_products_page_uses_service_terms():
    user = create_user("office-owner")
    organization = create_organization("orbit", facility_type=Facility.FacilityType.OFFICE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    grant_admin_navigation_entitlements(organization)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    response = client.get(f"/o/{organization.slug}/products/")

    assert response.status_code == 200
    assert b"Services" in response.content
    assert b"No services yet" in response.content
    assert b"Add service" in response.content
