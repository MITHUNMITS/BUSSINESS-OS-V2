from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.catalogue.models import Offering
from business_os.apps.catalogue.services import create_offering
from business_os.apps.core.models import AuditEvent, RecordStatus
from business_os.apps.entitlements.services import grant_entitlement
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


def create_organization(slug: str, *, facility_type: str) -> Organization:
    organization = Organization.objects.create(
        slug=slug,
        name=slug.title(),
        default_currency="AED",
    )
    Facility.objects.create(
        organization=organization,
        name=f"{slug.title()} Facility",
        code="primary",
        facility_type=facility_type,
    )
    grant_entitlement(organization=organization, code="catalogue.basic")
    return organization


def force_business_portal_login(client: Client, user) -> None:
    client.force_login(user)
    session = client.session
    session[PORTAL_SESSION_KEY] = PortalSessionScope.BUSINESS_ADMIN
    session.save()


def valid_payload(**overrides):
    payload = {
        "name": "Linen Wrap Dress",
        "code": "NOVA-001",
        "summary": "A lightweight seasonal bestseller.",
        "description": "Detailed catalogue copy for the public product page.",
        "base_price": "299.00",
        "currency": "AED",
        "status": RecordStatus.ACTIVE,
        "visible_on_website": "on",
        "whatsapp_inquiry_enabled": "on",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_create_online_product_with_variant_and_audit():
    user = create_user("online-owner")
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    get_response = client.get(f"/o/{organization.slug}/products/new/")
    post_response = client.post(
        f"/o/{organization.slug}/products/new/",
        valid_payload(code="nova-001"),
    )

    offering = Offering.objects.get(organization=organization, code="NOVA-001")
    variant = offering.variants.get()
    audit = AuditEvent.objects.get(action="catalogue.offering.created")
    assert get_response.status_code == 200
    assert b"Product name" in get_response.content
    assert b"Create product" in get_response.content
    assert post_response.status_code == 302
    assert post_response.headers["Location"] == f"/o/{organization.slug}/products/"
    assert offering.name == "Linen Wrap Dress"
    assert offering.slug == "linen-wrap-dress"
    assert offering.offering_type == Offering.OfferingType.PRODUCT
    assert offering.facility == facility
    assert offering.created_by == user
    assert variant.sku == "NOVA-001"
    assert variant.facility == facility
    assert audit.organization == organization
    assert audit.facility == facility
    assert audit.actor == user
    assert audit.target_id == str(offering.id)
    assert audit.after["code"] == "NOVA-001"
    assert audit.after["facility_type"] == Facility.FacilityType.ONLINE


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_admin_products_list_shows_draft_offerings():
    user = create_user("draft-owner")
    organization = create_organization("drafts", facility_type=Facility.FacilityType.ONLINE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    client.post(
        f"/o/{organization.slug}/products/new/",
        valid_payload(
            name="Private Preview Dress",
            code="PREVIEW-001",
            status=RecordStatus.DRAFT,
            visible_on_website="",
        ),
    )
    response = client.get(f"/o/{organization.slug}/products/")

    assert response.status_code == 200
    assert b"Private Preview Dress" in response.content
    assert b"draft" in response.content.lower()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_office_create_flow_uses_service_terms_and_service_type():
    user = create_user("office-owner")
    organization = create_organization("orbit", facility_type=Facility.FacilityType.OFFICE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    get_response = client.get(f"/o/{organization.slug}/products/new/")
    post_response = client.post(
        f"/o/{organization.slug}/products/new/",
        valid_payload(
            name="Consulting Retainer",
            code="CONSULT-001",
            base_price="1500.00",
        ),
    )

    offering = Offering.objects.get(organization=organization, code="CONSULT-001")
    assert get_response.status_code == 200
    assert b"Service name" in get_response.content
    assert b"Create service" in get_response.content
    assert post_response.status_code == 302
    assert offering.offering_type == Offering.OfferingType.SERVICE
    assert offering.base_price == Decimal("1500.00")


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_duplicate_code_returns_form_error_and_does_not_create_second_offering():
    user = create_user("duplicate-owner")
    organization = create_organization("dupes", facility_type=Facility.FacilityType.ONLINE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    create_offering(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Existing Dress",
        code="NOVA-001",
        base_price=Decimal("199.00"),
        currency="AED",
        created_by=user,
    )
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    response = client.post(
        f"/o/{organization.slug}/products/new/",
        valid_payload(name="Replacement Dress", code="nova-001"),
    )

    assert response.status_code == 200
    assert b"already exists" in response.content
    assert Offering.objects.filter(organization=organization, code="NOVA-001").count() == 1


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_cannot_create_offering_for_another_organization():
    user = create_user("scoped-owner")
    own_organization = create_organization("owned", facility_type=Facility.FacilityType.ONLINE)
    other_organization = create_organization("other", facility_type=Facility.FacilityType.ONLINE)
    Membership.objects.create(organization=own_organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    response = client.post(
        f"/o/{other_organization.slug}/products/new/",
        valid_payload(code="OTHER-001"),
    )

    assert response.status_code == 403
    assert not Offering.objects.filter(organization=other_organization).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_catalogue_admin_links_are_real_routes_not_dead_anchors():
    user = create_user("link-owner")
    organization = create_organization("links", facility_type=Facility.FacilityType.OFFICE)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)

    dashboard_response = client.get(f"/o/{organization.slug}/dashboard/")
    products_response = client.get(f"/o/{organization.slug}/products/")

    products_url = f'/o/{organization.slug}/products/'
    create_url = f'/o/{organization.slug}/products/new/'
    assert dashboard_response.status_code == 200
    assert products_response.status_code == 200
    assert f'href="{products_url}"'.encode() in dashboard_response.content
    assert f'href="{create_url}"'.encode() in dashboard_response.content
    assert f'href="{create_url}"'.encode() in products_response.content
    assert b"#admin-products" not in dashboard_response.content
