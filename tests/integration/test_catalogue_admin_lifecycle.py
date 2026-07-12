from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.catalogue.services import archive_offering, create_offering
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
        "name": "Updated Linen Dress",
        "code": "NOVA-999",
        "summary": "Updated short copy.",
        "description": "Updated long-form catalogue copy.",
        "base_price": "349.00",
        "currency": "AED",
        "status": RecordStatus.DRAFT,
    }
    payload.update(overrides)
    return payload


def create_member_client(*, username: str, organization: Organization):
    user = create_user(username)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)
    return client, user


def create_basic_offering(*, organization: Organization, user, code: str = "NOVA-001"):
    return create_offering(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Linen Wrap Dress",
        code=code,
        summary="Original short copy.",
        description="Original long copy.",
        base_price=Decimal("299.00"),
        currency="AED",
        created_by=user,
    )


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_view_and_edit_offering_with_audit_and_variant_sync():
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="lifecycle-owner", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)

    detail_response = client.get(f"/o/{organization.slug}/products/{offering.id}/")
    edit_response = client.get(f"/o/{organization.slug}/products/{offering.id}/edit/")
    post_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/edit/",
        valid_payload(visible_on_website="", whatsapp_inquiry_enabled=""),
    )

    offering.refresh_from_db()
    variant = offering.variants.get(is_default=True)
    audit = AuditEvent.objects.get(action="catalogue.offering.updated")
    assert detail_response.status_code == 200
    assert b"Linen Wrap Dress" in detail_response.content
    assert f'href="/o/{organization.slug}/products/{offering.id}/edit/"'.encode() in (
        detail_response.content
    )
    assert edit_response.status_code == 200
    assert b"Edit product" in edit_response.content
    assert post_response.status_code == 302
    assert post_response.headers["Location"] == f"/o/{organization.slug}/products/{offering.id}/"
    assert offering.name == "Updated Linen Dress"
    assert offering.code == "NOVA-999"
    assert offering.status == RecordStatus.DRAFT
    assert not offering.visible_on_website
    assert not offering.whatsapp_inquiry_enabled
    assert offering.updated_by == user
    assert variant.sku == "NOVA-999"
    assert variant.title == "Updated Linen Dress"
    assert variant.updated_by == user
    assert audit.organization == organization
    assert audit.actor == user
    assert audit.target_id == str(offering.id)
    assert audit.before["code"] == "NOVA-001"
    assert audit.after["code"] == "NOVA-999"
    assert audit.after["visible_on_website"] is False


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_edit_duplicate_code_returns_form_error_and_preserves_original_offering():
    organization = create_organization("dupes", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="duplicate-editor", organization=organization)
    create_basic_offering(organization=organization, user=user, code="NOVA-001")
    offering = create_basic_offering(organization=organization, user=user, code="NOVA-002")

    response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/edit/",
        valid_payload(name="Duplicate Attempt", code="nova-001"),
    )

    offering.refresh_from_db()
    assert response.status_code == 200
    assert b"already exists" in response.content
    assert offering.code == "NOVA-002"
    assert offering.name == "Linen Wrap Dress"
    assert not AuditEvent.objects.filter(action="catalogue.offering.updated").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_archive_is_post_only_hides_public_visibility_and_writes_audit():
    organization = create_organization("archive", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="archive-owner", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)

    get_response = client.get(f"/o/{organization.slug}/products/{offering.id}/archive/")
    post_response = client.post(f"/o/{organization.slug}/products/{offering.id}/archive/")

    offering.refresh_from_db()
    audit = AuditEvent.objects.get(action="catalogue.offering.archived")
    assert get_response.status_code == 405
    assert post_response.status_code == 302
    assert offering.status == RecordStatus.ARCHIVED
    assert not offering.visible_on_website
    assert offering.updated_by == user
    assert audit.before["status"] == RecordStatus.ACTIVE
    assert audit.after["status"] == RecordStatus.ARCHIVED
    assert not visible_offerings_for_organization(organization).filter(id=offering.id).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_restore_returns_archived_offering_as_draft_and_writes_audit():
    organization = create_organization("restore", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="restore-owner", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)
    archive_offering(organization=organization, offering=offering, archived_by=user)

    response = client.post(f"/o/{organization.slug}/products/{offering.id}/restore/")

    offering.refresh_from_db()
    audit = AuditEvent.objects.get(action="catalogue.offering.restored")
    assert response.status_code == 302
    assert offering.status == RecordStatus.DRAFT
    assert not offering.visible_on_website
    assert offering.updated_by == user
    assert audit.before["status"] == RecordStatus.ARCHIVED
    assert audit.after["status"] == RecordStatus.DRAFT
    assert not visible_offerings_for_organization(organization).filter(id=offering.id).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_cannot_access_other_organization_offering_lifecycle():
    own_organization = create_organization("owned", facility_type=Facility.FacilityType.ONLINE)
    other_organization = create_organization("other", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="scoped-editor", organization=own_organization)
    offering = create_basic_offering(organization=other_organization, user=user, code="OTHER-001")

    detail_response = client.get(f"/o/{own_organization.slug}/products/{offering.id}/")
    edit_response = client.post(
        f"/o/{own_organization.slug}/products/{offering.id}/edit/",
        valid_payload(code="LEAK-001"),
    )
    archive_response = client.post(
        f"/o/{own_organization.slug}/products/{offering.id}/archive/"
    )

    offering.refresh_from_db()
    assert detail_response.status_code == 404
    assert edit_response.status_code == 404
    assert archive_response.status_code == 404
    assert offering.code == "OTHER-001"
    assert offering.status == RecordStatus.ACTIVE


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_office_edit_flow_uses_service_terms():
    organization = create_organization("orbit", facility_type=Facility.FacilityType.OFFICE)
    client, user = create_member_client(username="office-editor", organization=organization)
    offering = create_basic_offering(organization=organization, user=user, code="CONSULT-001")

    response = client.get(f"/o/{organization.slug}/products/{offering.id}/edit/")

    assert response.status_code == 200
    assert b"Edit service" in response.content
    assert b"Service name" in response.content
