from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.catalogue.models import Collection, CollectionItem
from business_os.apps.catalogue.services import create_collection, create_offering
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
    grant_entitlement(organization=organization, code="catalogue.collections")
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


def create_basic_offering(*, organization: Organization, user, code: str, name: str):
    return create_offering(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name=name,
        code=code,
        base_price=Decimal("199.00"),
        currency="AED",
        created_by=user,
    )


def valid_collection_payload(**overrides):
    payload = {
        "name": "Summer Edit",
        "slug": "",
        "description": "Curated seasonal merchandising.",
        "offerings": [],
        "status": RecordStatus.ACTIVE,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_create_collection_with_offerings_and_audit():
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="collection-owner", organization=organization)
    first = create_basic_offering(
        organization=organization,
        user=user,
        code="NOVA-001",
        name="Linen Wrap Dress",
    )
    second = create_basic_offering(
        organization=organization,
        user=user,
        code="NOVA-002",
        name="Silk Occasion Set",
    )

    get_response = client.get(f"/o/{organization.slug}/collections/new/")
    post_response = client.post(
        f"/o/{organization.slug}/collections/new/",
        valid_collection_payload(offerings=[str(first.id), str(second.id)]),
    )

    collection = Collection.objects.get(organization=organization, slug="summer-edit")
    audit = AuditEvent.objects.get(action="catalogue.collection.created")
    list_response = client.get(f"/o/{organization.slug}/collections/")
    assert get_response.status_code == 200
    assert b"Collection name" in get_response.content
    assert b"Products in collection" in get_response.content
    assert post_response.status_code == 302
    assert post_response.headers["Location"] == (
        f"/o/{organization.slug}/collections/{collection.id}/"
    )
    assert collection.facility == facility
    assert collection.created_by == user
    assert list(collection.offerings.order_by("name")) == [first, second]
    assert CollectionItem.objects.filter(collection=collection).count() == 2
    assert audit.organization == organization
    assert audit.facility == facility
    assert audit.actor == user
    assert audit.after["slug"] == "summer-edit"
    assert audit.after["offering_count"] == 2
    assert list_response.status_code == 200
    assert b"Summer Edit" in list_response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_edit_collection_and_sync_membership():
    organization = create_organization("editcollection", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="collection-editor", organization=organization)
    first = create_basic_offering(
        organization=organization,
        user=user,
        code="NOVA-001",
        name="Linen Wrap Dress",
    )
    second = create_basic_offering(
        organization=organization,
        user=user,
        code="NOVA-002",
        name="Silk Occasion Set",
    )
    collection = create_collection(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Summer Edit",
        slug="summer-edit",
        offerings=[first],
        created_by=user,
    )

    get_response = client.get(f"/o/{organization.slug}/collections/{collection.id}/edit/")
    post_response = client.post(
        f"/o/{organization.slug}/collections/{collection.id}/edit/",
        valid_collection_payload(
            name="Occasion Edit",
            slug="occasion-edit",
            description="Updated collection copy.",
            offerings=[str(second.id)],
            status=RecordStatus.DRAFT,
        ),
    )

    collection.refresh_from_db()
    audit = AuditEvent.objects.get(action="catalogue.collection.updated")
    assert get_response.status_code == 200
    assert b"Save collection" in get_response.content
    assert post_response.status_code == 302
    assert collection.name == "Occasion Edit"
    assert collection.slug == "occasion-edit"
    assert collection.status == RecordStatus.DRAFT
    assert collection.updated_by == user
    assert list(collection.offerings.all()) == [second]
    assert not CollectionItem.objects.filter(collection=collection, offering=first).exists()
    assert audit.before["slug"] == "summer-edit"
    assert audit.before["offering_count"] == 1
    assert audit.after["slug"] == "occasion-edit"
    assert audit.after["offering_count"] == 1
    assert audit.after["offering_ids"] == [str(second.id)]


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_duplicate_collection_slug_returns_form_error_and_preserves_original():
    organization = create_organization("dupecollection", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="collection-dupe", organization=organization)
    create_collection(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Existing",
        slug="existing",
        created_by=user,
    )
    collection = create_collection(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Editable",
        slug="editable",
        created_by=user,
    )

    response = client.post(
        f"/o/{organization.slug}/collections/{collection.id}/edit/",
        valid_collection_payload(name="Duplicate", slug="existing"),
    )

    collection.refresh_from_db()
    assert response.status_code == 200
    assert b"already exists" in response.content
    assert collection.slug == "editable"
    assert collection.name == "Editable"
    assert not AuditEvent.objects.filter(action="catalogue.collection.updated").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_collection_archive_and_restore_are_post_only_and_audited():
    organization = create_organization("lifecollection", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="collection-life", organization=organization)
    collection = create_collection(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Seasonal",
        slug="seasonal",
        created_by=user,
    )

    archive_get = client.get(f"/o/{organization.slug}/collections/{collection.id}/archive/")
    archive_post = client.post(f"/o/{organization.slug}/collections/{collection.id}/archive/")
    collection.refresh_from_db()
    restore_get = client.get(f"/o/{organization.slug}/collections/{collection.id}/restore/")
    restore_post = client.post(f"/o/{organization.slug}/collections/{collection.id}/restore/")

    collection.refresh_from_db()
    archive_audit = AuditEvent.objects.get(action="catalogue.collection.archived")
    restore_audit = AuditEvent.objects.get(action="catalogue.collection.restored")
    assert archive_get.status_code == 405
    assert archive_post.status_code == 302
    assert restore_get.status_code == 405
    assert restore_post.status_code == 302
    assert collection.status == RecordStatus.DRAFT
    assert collection.updated_by == user
    assert archive_audit.before["status"] == RecordStatus.ACTIVE
    assert archive_audit.after["status"] == RecordStatus.ARCHIVED
    assert restore_audit.before["status"] == RecordStatus.ARCHIVED
    assert restore_audit.after["status"] == RecordStatus.DRAFT


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_cannot_access_other_organization_collection_lifecycle():
    own_organization = create_organization(
        "ownedcollection",
        facility_type=Facility.FacilityType.ONLINE,
    )
    other_organization = create_organization(
        "othercollection",
        facility_type=Facility.FacilityType.ONLINE,
    )
    client, user = create_member_client(username="collection-scope", organization=own_organization)
    collection = create_collection(
        organization=other_organization,
        facility=other_organization.facilities.get(code="primary"),
        name="Other",
        slug="other",
        created_by=user,
    )

    detail_response = client.get(f"/o/{own_organization.slug}/collections/{collection.id}/")
    edit_response = client.post(
        f"/o/{own_organization.slug}/collections/{collection.id}/edit/",
        valid_collection_payload(name="Leak", slug="leak"),
    )
    archive_response = client.post(
        f"/o/{own_organization.slug}/collections/{collection.id}/archive/"
    )

    collection.refresh_from_db()
    assert detail_response.status_code == 404
    assert edit_response.status_code == 404
    assert archive_response.status_code == 404
    assert collection.name == "Other"
    assert collection.status == RecordStatus.ACTIVE


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_collection_offering_membership_must_be_same_organization():
    organization = create_organization(
        "membercollection",
        facility_type=Facility.FacilityType.ONLINE,
    )
    other_organization = create_organization(
        "foreigncollection",
        facility_type=Facility.FacilityType.ONLINE,
    )
    client, user = create_member_client(username="collection-member", organization=organization)
    foreign = create_basic_offering(
        organization=other_organization,
        user=user,
        code="FOREIGN-001",
        name="Foreign Item",
    )

    response = client.post(
        f"/o/{organization.slug}/collections/new/",
        valid_collection_payload(offerings=[str(foreign.id)]),
    )

    assert response.status_code == 200
    assert b"Select a valid choice" in response.content
    assert not Collection.objects.filter(organization=organization, slug="summer-edit").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_office_collection_form_uses_service_terms_and_nav_route():
    organization = create_organization("orbit", facility_type=Facility.FacilityType.OFFICE)
    client, _user = create_member_client(username="collection-office", organization=organization)

    dashboard_response = client.get(f"/o/{organization.slug}/dashboard/")
    form_response = client.get(f"/o/{organization.slug}/collections/new/")

    assert dashboard_response.status_code == 200
    assert f'href="/o/{organization.slug}/collections/"'.encode() in dashboard_response.content
    assert form_response.status_code == 200
    assert b"Services in collection" in form_response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_offering_detail_shows_collection_membership():
    organization = create_organization(
        "detailcollection",
        facility_type=Facility.FacilityType.ONLINE,
    )
    client, user = create_member_client(username="collection-detail", organization=organization)
    offering = create_basic_offering(
        organization=organization,
        user=user,
        code="NOVA-001",
        name="Linen Wrap Dress",
    )
    create_collection(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Homepage Picks",
        slug="homepage-picks",
        offerings=[offering],
        created_by=user,
    )

    response = client.get(f"/o/{organization.slug}/products/{offering.id}/")

    assert response.status_code == 200
    assert b"Homepage Picks" in response.content
