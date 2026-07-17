from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.accounts.services import PORTAL_SESSION_KEY, PortalSessionScope
from business_os.apps.catalogue.models import OfferingVariant, OptionDefinition, OptionValue
from business_os.apps.catalogue.services import (
    create_offering,
    create_offering_variant,
    create_option_definition,
    create_option_value,
)
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


def create_organization(
    slug: str,
    *,
    facility_type: str,
    variants_entitlement: bool = True,
) -> Organization:
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
    if variants_entitlement:
        grant_entitlement(organization=organization, code="catalogue.variants")
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


def create_basic_offering(*, organization: Organization, user, code: str = "NOVA-001"):
    return create_offering(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Linen Wrap Dress",
        code=code,
        base_price=Decimal("299.00"),
        currency="AED",
        created_by=user,
    )


def option_payload(**overrides):
    payload = {
        "name": "Size",
        "code": "size",
        "sort_order": "10",
        "status": RecordStatus.ACTIVE,
    }
    payload.update(overrides)
    return payload


def option_value_payload(**overrides):
    payload = {
        "label": "Small",
        "value": "small",
        "color_hex": "",
        "sort_order": "10",
        "status": RecordStatus.ACTIVE,
    }
    payload.update(overrides)
    return payload


def variant_payload(**overrides):
    payload = {
        "sku": "NOVA-RED-S",
        "title": "Red / Small",
        "option_values": [],
        "price_override": "",
        "status": RecordStatus.ACTIVE,
        "stock_tracking_enabled": "on",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_create_option_value_variant_and_audit():
    organization = create_organization("nova", facility_type=Facility.FacilityType.ONLINE)
    facility = organization.facilities.get(code="primary")
    client, user = create_member_client(username="variant-owner", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)
    default_variant = offering.variants.get(is_default=True)

    option_get = client.get(f"/o/{organization.slug}/products/{offering.id}/options/new/")
    option_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/new/",
        option_payload(),
    )
    option = OptionDefinition.objects.get(organization=organization, code="size")
    value_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/values/new/",
        option_value_payload(),
    )
    option_value = OptionValue.objects.get(organization=organization, option=option)
    variant_get = client.get(f"/o/{organization.slug}/products/{offering.id}/variants/new/")
    variant_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/new/",
        variant_payload(option_values=[str(option_value.id)], price_override="319.00"),
    )

    variant = OfferingVariant.objects.get(organization=organization, sku="NOVA-RED-S")
    detail_response = client.get(f"/o/{organization.slug}/products/{offering.id}/")
    assert option_get.status_code == 200
    assert b"Option name" in option_get.content
    assert option_post.status_code == 302
    assert value_post.status_code == 302
    assert variant_get.status_code == 200
    assert b"Variant SKU" in variant_get.content
    assert variant_post.status_code == 302
    assert option.facility == facility
    assert option.created_by == user
    assert option_value.facility == facility
    assert variant.facility == facility
    assert variant.created_by == user
    assert variant.price_override == Decimal("319.00")
    assert list(variant.option_values.all()) == [option_value]
    default_variant.refresh_from_db()
    assert default_variant.is_default
    assert default_variant.sku == "NOVA-001"
    assert AuditEvent.objects.filter(action="catalogue.option.created").exists()
    assert AuditEvent.objects.filter(action="catalogue.option_value.created").exists()
    variant_audit = AuditEvent.objects.get(action="catalogue.variant.created")
    assert variant_audit.after["sku"] == "NOVA-RED-S"
    assert variant_audit.after["option_value_ids"] == [str(option_value.id)]
    assert detail_response.status_code == 200
    assert b"Red / Small" in detail_response.content
    assert b"Size: Small" in detail_response.content


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_option_and_value_duplicates_return_form_errors():
    organization = create_organization("dupevariant", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="option-dupe", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)
    option = create_option_definition(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Size",
        code="size",
        created_by=user,
    )
    create_option_value(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        option_definition=option,
        label="Small",
        value="small",
        created_by=user,
    )

    option_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/new/",
        option_payload(name="Duplicate Size", code="size"),
    )
    value_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/values/new/",
        option_value_payload(label="Duplicate Small", value="small"),
    )

    assert option_response.status_code == 200
    assert b"already exists" in option_response.content
    assert value_response.status_code == 200
    assert b"already has that value" in value_response.content
    assert OptionDefinition.objects.filter(organization=organization, code="size").count() == 1
    assert OptionValue.objects.filter(organization=organization, option=option).count() == 1


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_admin_can_edit_option_value_and_variant_with_audit():
    organization = create_organization("editvariant", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="variant-editor", organization=organization)
    facility = organization.facilities.get(code="primary")
    offering = create_basic_offering(organization=organization, user=user)
    option = create_option_definition(
        organization=organization,
        facility=facility,
        name="Size",
        code="size",
        created_by=user,
    )
    option_value = create_option_value(
        organization=organization,
        facility=facility,
        option_definition=option,
        label="Small",
        value="small",
        created_by=user,
    )
    variant = create_offering_variant(
        organization=organization,
        offering=offering,
        sku="NOVA-RED-S",
        title="Red / Small",
        option_values=[option_value],
        price_override=Decimal("319.00"),
        created_by=user,
    )

    option_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/edit/",
        option_payload(name="Fit", code="fit", sort_order="5", status=RecordStatus.DRAFT),
    )
    value_url = (
        f"/o/{organization.slug}/products/{offering.id}/options/"
        f"{option.id}/values/{option_value.id}"
    )
    value_response = client.post(
        f"{value_url}/edit/",
        option_value_payload(
            label="Medium",
            value="medium",
            color_hex="#111827",
            sort_order="5",
            status=RecordStatus.DRAFT,
        ),
    )
    variant_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}/edit/",
        variant_payload(
            sku="NOVA-RED-M",
            title="Red / Medium",
            option_values=[str(option_value.id)],
            price_override="",
            status=RecordStatus.DRAFT,
            stock_tracking_enabled="",
        ),
    )

    option.refresh_from_db()
    option_value.refresh_from_db()
    variant.refresh_from_db()
    assert option_response.status_code == 302
    assert value_response.status_code == 302
    assert variant_response.status_code == 302
    assert option.name == "Fit"
    assert option.code == "fit"
    assert option.status == RecordStatus.DRAFT
    assert option_value.label == "Medium"
    assert option_value.value == "medium"
    assert option_value.color_hex == "#111827"
    assert option_value.status == RecordStatus.DRAFT
    assert variant.sku == "NOVA-RED-M"
    assert variant.title == "Red / Medium"
    assert variant.price_override is None
    assert variant.status == RecordStatus.DRAFT
    assert not variant.stock_tracking_enabled
    assert AuditEvent.objects.filter(action="catalogue.option.updated").exists()
    assert AuditEvent.objects.filter(action="catalogue.option_value.updated").exists()
    assert AuditEvent.objects.filter(action="catalogue.variant.updated").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_variant_duplicate_sku_and_cross_tenant_value_are_rejected():
    organization = create_organization("variantdupe", facility_type=Facility.FacilityType.ONLINE)
    other_organization = create_organization(
        "foreignvariant",
        facility_type=Facility.FacilityType.ONLINE,
    )
    client, user = create_member_client(username="variant-dupe", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)
    option = create_option_definition(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        name="Size",
        code="size",
        created_by=user,
    )
    option_value = create_option_value(
        organization=organization,
        facility=organization.facilities.get(code="primary"),
        option_definition=option,
        label="Small",
        value="small",
        created_by=user,
    )
    create_offering_variant(
        organization=organization,
        offering=offering,
        sku="NOVA-RED-S",
        option_values=[option_value],
        created_by=user,
    )
    foreign_option = create_option_definition(
        organization=other_organization,
        facility=other_organization.facilities.get(code="primary"),
        name="Foreign Size",
        code="foreign-size",
        created_by=user,
    )
    foreign_value = create_option_value(
        organization=other_organization,
        facility=other_organization.facilities.get(code="primary"),
        option_definition=foreign_option,
        label="Foreign",
        value="foreign",
        created_by=user,
    )

    duplicate_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/new/",
        variant_payload(option_values=[str(option_value.id)]),
    )
    foreign_response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/new/",
        variant_payload(sku="NOVA-BLUE-S", option_values=[str(foreign_value.id)]),
    )

    assert duplicate_response.status_code == 200
    assert b"already exists" in duplicate_response.content
    assert foreign_response.status_code == 200
    assert b"Select a valid choice" in foreign_response.content
    assert not OfferingVariant.objects.filter(organization=organization, sku="NOVA-BLUE-S").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_variant_rejects_multiple_values_from_the_same_option():
    organization = create_organization("sameoption", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="same-option", organization=organization)
    facility = organization.facilities.get(code="primary")
    offering = create_basic_offering(organization=organization, user=user)
    option = create_option_definition(
        organization=organization,
        facility=facility,
        name="Size",
        code="size",
        created_by=user,
    )
    small = create_option_value(
        organization=organization,
        facility=facility,
        option_definition=option,
        label="Small",
        value="small",
        created_by=user,
    )
    medium = create_option_value(
        organization=organization,
        facility=facility,
        option_definition=option,
        label="Medium",
        value="medium",
        created_by=user,
    )

    response = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/new/",
        variant_payload(option_values=[str(small.id), str(medium.id)]),
    )

    assert response.status_code == 200
    assert b"Choose only one value for each option" in response.content
    assert not OfferingVariant.objects.filter(organization=organization, sku="NOVA-RED-S").exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_business_member_cannot_access_other_organization_variant_workflows():
    own_organization = create_organization(
        "ownedvariant",
        facility_type=Facility.FacilityType.ONLINE,
    )
    other_organization = create_organization(
        "othervariant",
        facility_type=Facility.FacilityType.ONLINE,
    )
    client, user = create_member_client(username="variant-scope", organization=own_organization)
    own_offering = create_basic_offering(organization=own_organization, user=user)
    other_offering = create_basic_offering(
        organization=other_organization,
        user=user,
        code="OTHER-001",
    )
    other_option = create_option_definition(
        organization=other_organization,
        facility=other_organization.facilities.get(code="primary"),
        name="Other Size",
        code="other-size",
        created_by=user,
    )
    other_value = create_option_value(
        organization=other_organization,
        facility=other_organization.facilities.get(code="primary"),
        option_definition=other_option,
        label="Other",
        value="other",
        created_by=user,
    )
    other_variant = create_offering_variant(
        organization=other_organization,
        offering=other_offering,
        sku="OTHER-S",
        option_values=[other_value],
        created_by=user,
    )

    other_org_response = client.post(
        f"/o/{other_organization.slug}/products/{other_offering.id}/variants/new/",
        variant_payload(sku="LEAK-001"),
    )
    option_response = client.get(
        f"/o/{own_organization.slug}/products/{own_offering.id}/options/{other_option.id}/edit/"
    )
    variant_response = client.get(
        f"/o/{own_organization.slug}/products/{own_offering.id}/variants/{other_variant.id}/edit/"
    )

    assert other_org_response.status_code == 403
    assert option_response.status_code == 404
    assert variant_response.status_code == 404
    assert not OfferingVariant.objects.filter(
        organization=own_organization,
        sku="LEAK-001",
    ).exists()


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_catalogue_variants_entitlement_is_required_for_variant_routes():
    organization = create_organization(
        "basiccatalogue",
        facility_type=Facility.FacilityType.ONLINE,
        variants_entitlement=False,
    )
    client, user = create_member_client(username="no-variants", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)

    detail_response = client.get(f"/o/{organization.slug}/products/{offering.id}/")
    create_response = client.get(f"/o/{organization.slug}/products/{offering.id}/variants/new/")

    assert detail_response.status_code == 200
    assert b"Add variant" not in detail_response.content
    assert create_response.status_code == 403


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_variant_archive_restore_are_post_only_and_keep_default_variant():
    organization = create_organization("variantlife", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="variant-life", organization=organization)
    offering = create_basic_offering(organization=organization, user=user)
    default_variant = offering.variants.get(is_default=True)
    variant = create_offering_variant(
        organization=organization,
        offering=offering,
        sku="NOVA-RED-S",
        title="Red / Small",
        created_by=user,
    )

    archive_get = client.get(
        f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}/archive/"
    )
    archive_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}/archive/"
    )
    variant.refresh_from_db()
    restore_get = client.get(
        f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}/restore/"
    )
    restore_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}/restore/"
    )

    variant.refresh_from_db()
    default_variant.refresh_from_db()
    archive_audit = AuditEvent.objects.get(action="catalogue.variant.archived")
    restore_audit = AuditEvent.objects.get(action="catalogue.variant.restored")
    assert archive_get.status_code == 405
    assert archive_post.status_code == 302
    assert restore_get.status_code == 405
    assert restore_post.status_code == 302
    assert variant.status == RecordStatus.DRAFT
    assert variant.updated_by == user
    assert default_variant.is_default
    assert default_variant.status == RecordStatus.ACTIVE
    assert archive_audit.before["status"] == RecordStatus.ACTIVE
    assert archive_audit.after["status"] == RecordStatus.ARCHIVED
    assert restore_audit.before["status"] == RecordStatus.ARCHIVED
    assert restore_audit.after["status"] == RecordStatus.DRAFT


@pytest.mark.django_db
@override_settings(**HOST_SETTINGS)
def test_option_and_value_archive_restore_are_post_only_and_audited():
    organization = create_organization("optionlife", facility_type=Facility.FacilityType.ONLINE)
    client, user = create_member_client(username="option-life", organization=organization)
    facility = organization.facilities.get(code="primary")
    offering = create_basic_offering(organization=organization, user=user)
    option = create_option_definition(
        organization=organization,
        facility=facility,
        name="Size",
        code="size",
        created_by=user,
    )
    option_value = create_option_value(
        organization=organization,
        facility=facility,
        option_definition=option,
        label="Small",
        value="small",
        created_by=user,
    )

    option_archive_get = client.get(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/archive/"
    )
    option_archive_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/archive/"
    )
    option.refresh_from_db()
    option_restore_get = client.get(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/restore/"
    )
    option_restore_post = client.post(
        f"/o/{organization.slug}/products/{offering.id}/options/{option.id}/restore/"
    )
    value_url = (
        f"/o/{organization.slug}/products/{offering.id}/options/"
        f"{option.id}/values/{option_value.id}"
    )
    value_archive_get = client.get(
        f"{value_url}/archive/"
    )
    value_archive_post = client.post(
        f"{value_url}/archive/"
    )
    option_value.refresh_from_db()
    value_restore_get = client.get(
        f"{value_url}/restore/"
    )
    value_restore_post = client.post(
        f"{value_url}/restore/"
    )

    option.refresh_from_db()
    option_value.refresh_from_db()
    assert option_archive_get.status_code == 405
    assert option_archive_post.status_code == 302
    assert option_restore_get.status_code == 405
    assert option_restore_post.status_code == 302
    assert value_archive_get.status_code == 405
    assert value_archive_post.status_code == 302
    assert value_restore_get.status_code == 405
    assert value_restore_post.status_code == 302
    assert option.status == RecordStatus.DRAFT
    assert option_value.status == RecordStatus.DRAFT
    assert AuditEvent.objects.filter(action="catalogue.option.archived").exists()
    assert AuditEvent.objects.filter(action="catalogue.option.restored").exists()
    assert AuditEvent.objects.filter(action="catalogue.option_value.archived").exists()
    assert AuditEvent.objects.filter(action="catalogue.option_value.restored").exists()
