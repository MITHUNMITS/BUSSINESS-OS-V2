from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.catalogue.models import Category, Offering
from business_os.apps.catalogue.services import create_category
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


def create_member_client(*, username: str, organization: Organization):
    user = create_user(username)
    Membership.objects.create(organization=organization, user=user, is_owner=True)
    client = Client(HTTP_HOST="app.businessos.local")
    force_business_portal_login(client, user)
    return client, user


def valid_category_payload(**overrides):
    payload = {
        "name": "Summer Dresses",
        "slug": "",
        "parent": "",
        "description": "Seasonal catalogue grouping.",
        "sort_order": "10",
        "status": RecordStatus.ACTIVE,
    }
    payload.update(overrides)
    return payload


def valid_offering_payload(**overrides):
    payload = {
        "name": "Linen Wrap Dress",
        "code": "NOVA-001",
        "summary": "A lightweight seasonal bestseller.",
        "description": "Detailed catalogue copy.",
        "category": "",
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
def test_business_admin_can_create_category_with_auto_slug_and_audit():
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-owner", organization=organization)

    get_response = client.get(f"/o/{organization.slug}/categories/new/")
    post_response = client.post(
        f"/o/{organization.slug}/categories/new/",
        valid_category_payload(),
    )

    category = Category.objects.get(organization=organization, slug="summer-dresses")
    audit = AuditEvent.objects.get(action="catalogue.category.created")
    list_response = client.get(f"/o/{organization.slug}/categories/")
    assert get_response.status_code == 200
    assert b"Category name" in get_response.content
    assert b"Create category" in get_response.content
    assert post_response.status_code == 302
    assert post_response.headers["Location"] == f"/o/{organization.slug}/categories/{category.id}/"
    assert category.name == "Summer Dresses"
    assert category.facility == facility
    assert category.created_by == user
    assert audit.organization == organization
    assert audit.facility == facility
    assert audit.actor == user
    assert audit.target_id == str(category.id)
    assert audit.after["slug"] == "summer-dresses"
    assert list_response.status_code == 200
    assert b"Summer Dresses" in list_response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_office_category_pages_use_service_area_terms():
    organization = create_organization("orbit", facility_type=Facility.FacilityType.OFFICE)
    client, _user = create_member_client(username="office-category", organization=organization)

    list_response = client.get(f"/o/{organization.slug}/categories/")
    create_response = client.get(f"/o/{organization.slug}/categories/new/")

    assert list_response.status_code == 200
    assert b"Service areas" in list_response.content
    assert b"No service areas yet" in list_response.content
    assert create_response.status_code == 200
    assert b"Service area name" in create_response.content
    assert b"Create service area" in create_response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_edit_category_parent_and_audit_changes():
    organization = create_organization("editcat", facility_type=Facility.FacilityType.RETAIL)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-editor", organization=organization)
    parent = create_category(
        organization=organization,
        facility=facility,
        name="Women",
        slug="women",
        sort_order=1,
        created_by=user,
    )
    category = create_category(
        organization=organization,
        facility=facility,
        name="Dresses",
        slug="dresses",
        sort_order=2,
        created_by=user,
    )

    get_response = client.get(f"/o/{organization.slug}/categories/{category.id}/edit/")
    post_response = client.post(
        f"/o/{organization.slug}/categories/{category.id}/edit/",
        valid_category_payload(
            name="Occasion Dresses",
            slug="occasion-dresses",
            parent=str(parent.id),
            description="Edited department copy.",
            sort_order="5",
            status=RecordStatus.DRAFT,
        ),
    )

    category.refresh_from_db()
    audit = AuditEvent.objects.get(action="catalogue.category.updated")
    assert get_response.status_code == 200
    assert b"Department name" in get_response.content
    assert b"Save department" in get_response.content
    assert post_response.status_code == 302
    assert category.name == "Occasion Dresses"
    assert category.slug == "occasion-dresses"
    assert category.parent == parent
    assert category.sort_order == 5
    assert category.status == RecordStatus.DRAFT
    assert category.updated_by == user
    assert audit.before["slug"] == "dresses"
    assert audit.after["slug"] == "occasion-dresses"
    assert audit.after["parent_id"] == str(parent.id)


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_duplicate_category_slug_returns_form_error_and_preserves_original():
    organization = create_organization("dupecat", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-dupe", organization=organization)
    create_category(
        organization=organization,
        facility=facility,
        name="Existing",
        slug="existing",
        created_by=user,
    )
    category = create_category(
        organization=organization,
        facility=facility,
        name="Editable",
        slug="editable",
        created_by=user,
    )

    response = client.post(
        f"/o/{organization.slug}/categories/{category.id}/edit/",
        valid_category_payload(name="Duplicate", slug="existing"),
    )

    category.refresh_from_db()
    assert response.status_code == 200
    assert b"already exists" in response.content
    assert category.slug == "editable"
    assert category.name == "Editable"
    assert not AuditEvent.objects.filter(action="catalogue.category.updated").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_category_archive_and_restore_are_post_only_and_audited():
    organization = create_organization("lifecat", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-life", organization=organization)
    category = create_category(
        organization=organization,
        facility=facility,
        name="Seasonal",
        slug="seasonal",
        created_by=user,
    )

    archive_get = client.get(f"/o/{organization.slug}/categories/{category.id}/archive/")
    archive_post = client.post(f"/o/{organization.slug}/categories/{category.id}/archive/")
    category.refresh_from_db()
    restore_get = client.get(f"/o/{organization.slug}/categories/{category.id}/restore/")
    restore_post = client.post(f"/o/{organization.slug}/categories/{category.id}/restore/")

    category.refresh_from_db()
    archive_audit = AuditEvent.objects.get(action="catalogue.category.archived")
    restore_audit = AuditEvent.objects.get(action="catalogue.category.restored")
    assert archive_get.status_code == 405
    assert archive_post.status_code == 302
    assert restore_get.status_code == 405
    assert restore_post.status_code == 302
    assert category.status == RecordStatus.DRAFT
    assert category.updated_by == user
    assert archive_audit.before["status"] == RecordStatus.ACTIVE
    assert archive_audit.after["status"] == RecordStatus.ARCHIVED
    assert restore_audit.before["status"] == RecordStatus.ARCHIVED
    assert restore_audit.after["status"] == RecordStatus.DRAFT


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_cannot_access_other_organization_category_lifecycle():
    own_organization = create_organization("ownedcat", facility_type=Facility.FacilityType.ONLINE)
    other_organization = create_organization("othercat", facility_type=Facility.FacilityType.ONLINE)
    other_facility = other_organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-scope", organization=own_organization)
    category = create_category(
        organization=other_organization,
        facility=other_facility,
        name="Other",
        slug="other",
        created_by=user,
    )

    detail_response = client.get(f"/o/{own_organization.slug}/categories/{category.id}/")
    edit_response = client.post(
        f"/o/{own_organization.slug}/categories/{category.id}/edit/",
        valid_category_payload(name="Leak", slug="leak"),
    )
    archive_response = client.post(
        f"/o/{own_organization.slug}/categories/{category.id}/archive/"
    )

    category.refresh_from_db()
    assert detail_response.status_code == 404
    assert edit_response.status_code == 404
    assert archive_response.status_code == 404
    assert category.name == "Other"
    assert category.status == RecordStatus.ACTIVE


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_category_parent_must_be_in_same_organization():
    organization = create_organization("parentcat", facility_type=Facility.FacilityType.ONLINE)
    other_organization = create_organization(
        "foreigncat",
        facility_type=Facility.FacilityType.ONLINE,
    )
    other_facility = other_organization.facilities.get(code="primary")
    client, user = create_member_client(username="parent-scope", organization=organization)
    foreign_parent = create_category(
        organization=other_organization,
        facility=other_facility,
        name="Foreign",
        slug="foreign",
        created_by=user,
    )

    response = client.post(
        f"/o/{organization.slug}/categories/new/",
        valid_category_payload(parent=str(foreign_parent.id)),
    )

    assert response.status_code == 200
    assert b"Select a valid choice" in response.content
    assert not Category.objects.filter(organization=organization, slug="summer-dresses").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_offering_create_and_edit_can_assign_category():
    organization = create_organization("wirecat", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="category-wire", organization=organization)
    category = create_category(
        organization=organization,
        facility=facility,
        name="Summer",
        slug="summer",
        created_by=user,
    )
    replacement = create_category(
        organization=organization,
        facility=facility,
        name="Featured",
        slug="featured",
        created_by=user,
    )

    create_response = client.post(
        f"/o/{organization.slug}/products/new/",
        valid_offering_payload(category=str(category.id)),
    )
    offering = Offering.objects.get(organization=organization, code="NOVA-001")
    edit_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/edit/",
        valid_offering_payload(
            name="Edited Dress",
            code="NOVA-002",
            category=str(replacement.id),
            base_price="329.00",
        ),
    )

    offering.refresh_from_db()
    assert create_response.status_code == 302
    assert edit_response.status_code == 302
    assert offering.category == replacement
    assert offering.base_price == Decimal("329.00")
