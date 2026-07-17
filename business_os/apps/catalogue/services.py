from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.text import slugify

from business_os.apps.catalogue.models import (
    Category,
    Collection,
    CollectionItem,
    Offering,
    OfferingVariant,
    OptionDefinition,
    OptionValue,
)
from business_os.apps.core.models import RecordStatus


@transaction.atomic
def create_offering(
    *,
    organization,
    name: str,
    code: str,
    base_price,
    currency: str,
    offering_type: str = Offering.OfferingType.PRODUCT,
    summary: str = "",
    description: str = "",
    category=None,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    visible_on_website: bool = True,
    whatsapp_inquiry_enabled: bool = True,
    created_by=None,
) -> Offering:
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    _validate_category_scope(organization=organization, facility=facility, category=category)

    payload = _clean_offering_payload(
        name=name,
        code=code,
        base_price=base_price,
        currency=currency,
        offering_type=offering_type,
        status=status,
    )
    if Offering.objects.filter(organization=organization, code__iexact=payload["code"]).exists():
        raise ValueError("An offering with this code already exists.")
    if OfferingVariant.objects.filter(
        organization=organization,
        sku__iexact=payload["code"],
    ).exists():
        raise ValueError("A variant with this SKU already exists.")

    product = Offering.objects.create(
        organization=organization,
        facility=facility,
        category=category,
        offering_type=payload["offering_type"],
        name=payload["name"],
        slug=_unique_offering_slug(
            organization=organization,
            name=payload["name"],
            code=payload["code"],
        ),
        code=payload["code"],
        summary=summary.strip(),
        description=description.strip(),
        base_price=payload["base_price"],
        currency=payload["currency"],
        visible_on_website=visible_on_website,
        whatsapp_inquiry_enabled=whatsapp_inquiry_enabled,
        status=payload["status"],
        created_by=created_by,
    )
    OfferingVariant.objects.create(
        organization=organization,
        facility=facility,
        offering=product,
        sku=payload["code"],
        title=payload["name"],
        is_default=True,
        created_by=created_by,
    )
    return product


@transaction.atomic
def update_offering(
    *,
    organization,
    offering,
    name: str,
    code: str,
    base_price,
    currency: str,
    offering_type: str = Offering.OfferingType.PRODUCT,
    summary: str = "",
    description: str = "",
    category=None,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    visible_on_website: bool = True,
    whatsapp_inquiry_enabled: bool = True,
    updated_by=None,
) -> Offering:
    if offering.organization_id != organization.id:
        raise PermissionDenied("Offering does not belong to this organization.")
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    _validate_category_scope(organization=organization, facility=facility, category=category)

    current = Offering.objects.select_for_update().get(
        organization=organization,
        id=offering.id,
    )
    payload = _clean_offering_payload(
        name=name,
        code=code,
        base_price=base_price,
        currency=currency,
        offering_type=offering_type,
        status=status,
    )
    if (
        Offering.objects.filter(organization=organization, code__iexact=payload["code"])
        .exclude(id=current.id)
        .exists()
    ):
        raise ValueError("An offering with this code already exists.")

    default_variant = _default_variant_for_offering(current, lock=True)
    variant_conflicts = OfferingVariant.objects.filter(
        organization=organization,
        sku__iexact=payload["code"],
    )
    if default_variant is not None:
        variant_conflicts = variant_conflicts.exclude(id=default_variant.id)
    if variant_conflicts.exists():
        raise ValueError("A variant with this SKU already exists.")

    current.facility = facility
    current.category = category
    current.offering_type = payload["offering_type"]
    current.name = payload["name"]
    current.slug = _unique_offering_slug(
        organization=organization,
        name=payload["name"],
        code=payload["code"],
        exclude=current,
    )
    current.code = payload["code"]
    current.summary = summary.strip()
    current.description = description.strip()
    current.base_price = payload["base_price"]
    current.currency = payload["currency"]
    current.visible_on_website = visible_on_website
    current.whatsapp_inquiry_enabled = whatsapp_inquiry_enabled
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "category",
            "offering_type",
            "name",
            "slug",
            "code",
            "summary",
            "description",
            "base_price",
            "currency",
            "visible_on_website",
            "whatsapp_inquiry_enabled",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    _sync_default_variant(
        organization=organization,
        offering=current,
        facility=facility,
        code=payload["code"],
        title=payload["name"],
        default_variant=default_variant,
        user=updated_by,
    )
    return current


@transaction.atomic
def create_category(
    *,
    organization,
    name: str,
    slug: str = "",
    parent=None,
    description: str = "",
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    created_by=None,
) -> Category:
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    _validate_category_parent(
        organization=organization,
        facility=facility,
        parent=parent,
    )
    payload = _clean_category_payload(
        organization=organization,
        name=name,
        slug=slug,
        sort_order=sort_order,
        status=status,
    )
    return Category.objects.create(
        organization=organization,
        facility=facility,
        parent=parent,
        name=payload["name"],
        slug=payload["slug"],
        description=description.strip(),
        sort_order=payload["sort_order"],
        status=payload["status"],
        created_by=created_by,
    )


@transaction.atomic
def update_category(
    *,
    organization,
    category,
    name: str,
    slug: str = "",
    parent=None,
    description: str = "",
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    updated_by=None,
) -> Category:
    if category.organization_id != organization.id:
        raise PermissionDenied("Category does not belong to this organization.")
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")

    current = Category.objects.select_for_update().get(
        organization=organization,
        id=category.id,
    )
    _validate_category_parent(
        organization=organization,
        facility=facility,
        parent=parent,
        category=current,
    )
    payload = _clean_category_payload(
        organization=organization,
        name=name,
        slug=slug,
        sort_order=sort_order,
        status=status,
        exclude=current,
    )
    current.facility = facility
    current.parent = parent
    current.name = payload["name"]
    current.slug = payload["slug"]
    current.description = description.strip()
    current.sort_order = payload["sort_order"]
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "parent",
            "name",
            "slug",
            "description",
            "sort_order",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    return current


@transaction.atomic
def create_collection(
    *,
    organization,
    name: str,
    slug: str = "",
    description: str = "",
    offerings=None,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    created_by=None,
) -> Collection:
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    selected_offerings = list(offerings or [])
    _validate_collection_offerings(
        organization=organization,
        facility=facility,
        offerings=selected_offerings,
    )
    payload = _clean_collection_payload(
        organization=organization,
        name=name,
        slug=slug,
        status=status,
    )
    collection = Collection.objects.create(
        organization=organization,
        facility=facility,
        name=payload["name"],
        slug=payload["slug"],
        description=description.strip(),
        status=payload["status"],
        created_by=created_by,
    )
    _sync_collection_offerings(
        organization=organization,
        collection=collection,
        facility=facility,
        offerings=selected_offerings,
        user=created_by,
    )
    return collection


@transaction.atomic
def update_collection(
    *,
    organization,
    collection,
    name: str,
    slug: str = "",
    description: str = "",
    offerings=None,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    updated_by=None,
) -> Collection:
    if collection.organization_id != organization.id:
        raise PermissionDenied("Collection does not belong to this organization.")
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")

    current = Collection.objects.select_for_update().get(
        organization=organization,
        id=collection.id,
    )
    selected_offerings = list(offerings or [])
    _validate_collection_offerings(
        organization=organization,
        facility=facility,
        offerings=selected_offerings,
    )
    payload = _clean_collection_payload(
        organization=organization,
        name=name,
        slug=slug,
        status=status,
        exclude=current,
    )
    current.facility = facility
    current.name = payload["name"]
    current.slug = payload["slug"]
    current.description = description.strip()
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "name",
            "slug",
            "description",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    _sync_collection_offerings(
        organization=organization,
        collection=current,
        facility=facility,
        offerings=selected_offerings,
        user=updated_by,
    )
    return current


@transaction.atomic
def create_option_definition(
    *,
    organization,
    name: str,
    code: str,
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    created_by=None,
) -> OptionDefinition:
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    payload = _clean_option_payload(
        organization=organization,
        name=name,
        code=code,
        sort_order=sort_order,
        status=status,
    )
    return OptionDefinition.objects.create(
        organization=organization,
        facility=facility,
        name=payload["name"],
        code=payload["code"],
        sort_order=payload["sort_order"],
        status=payload["status"],
        created_by=created_by,
    )


@transaction.atomic
def update_option_definition(
    *,
    organization,
    option_definition,
    name: str,
    code: str,
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    updated_by=None,
) -> OptionDefinition:
    if option_definition.organization_id != organization.id:
        raise PermissionDenied("Option does not belong to this organization.")
    if facility is not None and facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")
    current = OptionDefinition.objects.select_for_update().get(
        organization=organization,
        id=option_definition.id,
    )
    payload = _clean_option_payload(
        organization=organization,
        name=name,
        code=code,
        sort_order=sort_order,
        status=status,
        exclude=current,
    )
    current.facility = facility
    current.name = payload["name"]
    current.code = payload["code"]
    current.sort_order = payload["sort_order"]
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "name",
            "code",
            "sort_order",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    return current


@transaction.atomic
def create_option_value(
    *,
    organization,
    option_definition,
    label: str,
    value: str,
    color_hex: str = "",
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    created_by=None,
) -> OptionValue:
    _validate_option_definition_scope(
        organization=organization,
        facility=facility,
        option_definition=option_definition,
    )
    payload = _clean_option_value_payload(
        organization=organization,
        option_definition=option_definition,
        label=label,
        value=value,
        color_hex=color_hex,
        sort_order=sort_order,
        status=status,
    )
    return OptionValue.objects.create(
        organization=organization,
        facility=facility,
        option=option_definition,
        label=payload["label"],
        value=payload["value"],
        color_hex=payload["color_hex"],
        sort_order=payload["sort_order"],
        status=payload["status"],
        created_by=created_by,
    )


@transaction.atomic
def update_option_value(
    *,
    organization,
    option_value,
    label: str,
    value: str,
    color_hex: str = "",
    sort_order: int = 0,
    facility=None,
    status: str = RecordStatus.ACTIVE,
    updated_by=None,
) -> OptionValue:
    if option_value.organization_id != organization.id:
        raise PermissionDenied("Option value does not belong to this organization.")
    current = (
        OptionValue.objects.select_for_update()
        .select_related("option")
        .get(organization=organization, id=option_value.id)
    )
    _validate_option_definition_scope(
        organization=organization,
        facility=facility,
        option_definition=current.option,
    )
    payload = _clean_option_value_payload(
        organization=organization,
        option_definition=current.option,
        label=label,
        value=value,
        color_hex=color_hex,
        sort_order=sort_order,
        status=status,
        exclude=current,
    )
    current.facility = facility
    current.label = payload["label"]
    current.value = payload["value"]
    current.color_hex = payload["color_hex"]
    current.sort_order = payload["sort_order"]
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "label",
            "value",
            "color_hex",
            "sort_order",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    return current


@transaction.atomic
def create_offering_variant(
    *,
    organization,
    offering,
    sku: str,
    title: str = "",
    option_values=None,
    price_override=None,
    stock_tracking_enabled: bool = True,
    status: str = RecordStatus.ACTIVE,
    created_by=None,
) -> OfferingVariant:
    if offering.organization_id != organization.id:
        raise PermissionDenied("Offering does not belong to this organization.")
    selected_values = _validate_variant_option_values(
        organization=organization,
        facility=offering.facility,
        option_values=list(option_values or []),
    )
    payload = _clean_variant_payload(
        organization=organization,
        sku=sku,
        title=title,
        price_override=price_override,
        stock_tracking_enabled=stock_tracking_enabled,
        status=status,
    )
    variant = OfferingVariant.objects.create(
        organization=organization,
        facility=offering.facility,
        offering=offering,
        sku=payload["sku"],
        title=payload["title"],
        price_override=payload["price_override"],
        stock_tracking_enabled=payload["stock_tracking_enabled"],
        status=payload["status"],
        is_default=False,
        created_by=created_by,
    )
    variant.option_values.set(selected_values)
    return variant


@transaction.atomic
def update_offering_variant(
    *,
    organization,
    variant,
    sku: str,
    title: str = "",
    option_values=None,
    price_override=None,
    stock_tracking_enabled: bool = True,
    status: str = RecordStatus.ACTIVE,
    updated_by=None,
) -> OfferingVariant:
    if variant.organization_id != organization.id:
        raise PermissionDenied("Variant does not belong to this organization.")
    current = (
        OfferingVariant.objects.select_for_update()
        .select_related("offering", "facility")
        .get(organization=organization, id=variant.id)
    )
    if current.is_default:
        raise ValueError("The default variant is managed from the offering form.")
    selected_values = _validate_variant_option_values(
        organization=organization,
        facility=current.offering.facility,
        option_values=list(option_values or []),
    )
    payload = _clean_variant_payload(
        organization=organization,
        sku=sku,
        title=title,
        price_override=price_override,
        stock_tracking_enabled=stock_tracking_enabled,
        status=status,
        exclude=current,
    )
    current.facility = current.offering.facility
    current.sku = payload["sku"]
    current.title = payload["title"]
    current.price_override = payload["price_override"]
    current.stock_tracking_enabled = payload["stock_tracking_enabled"]
    current.status = payload["status"]
    current.updated_by = updated_by
    current.save(
        update_fields=[
            "facility",
            "sku",
            "title",
            "price_override",
            "stock_tracking_enabled",
            "status",
            "updated_by",
            "updated_at",
        ]
    )
    current.option_values.set(selected_values)
    return current


@transaction.atomic
def archive_option_definition(
    *,
    organization,
    option_definition,
    archived_by=None,
) -> OptionDefinition:
    current = _locked_option_for_organization(
        organization=organization,
        option_definition=option_definition,
    )
    current.status = RecordStatus.ARCHIVED
    current.updated_by = archived_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_option_definition(
    *,
    organization,
    option_definition,
    restored_by=None,
) -> OptionDefinition:
    current = _locked_option_for_organization(
        organization=organization,
        option_definition=option_definition,
    )
    current.status = RecordStatus.DRAFT
    current.updated_by = restored_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def archive_option_value(*, organization, option_value, archived_by=None) -> OptionValue:
    current = _locked_option_value_for_organization(
        organization=organization,
        option_value=option_value,
    )
    current.status = RecordStatus.ARCHIVED
    current.updated_by = archived_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_option_value(*, organization, option_value, restored_by=None) -> OptionValue:
    current = _locked_option_value_for_organization(
        organization=organization,
        option_value=option_value,
    )
    current.status = RecordStatus.DRAFT
    current.updated_by = restored_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def archive_offering_variant(*, organization, variant, archived_by=None) -> OfferingVariant:
    current = _locked_variant_for_organization(organization=organization, variant=variant)
    if current.is_default:
        raise ValueError("The default variant cannot be archived.")
    current.status = RecordStatus.ARCHIVED
    current.updated_by = archived_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_offering_variant(*, organization, variant, restored_by=None) -> OfferingVariant:
    current = _locked_variant_for_organization(organization=organization, variant=variant)
    if current.is_default:
        raise ValueError("The default variant is restored through the offering lifecycle.")
    current.status = RecordStatus.DRAFT
    current.updated_by = restored_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def archive_collection(*, organization, collection, archived_by=None) -> Collection:
    current = _locked_collection_for_organization(
        organization=organization,
        collection=collection,
    )
    current.status = RecordStatus.ARCHIVED
    current.updated_by = archived_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_collection(*, organization, collection, restored_by=None) -> Collection:
    current = _locked_collection_for_organization(
        organization=organization,
        collection=collection,
    )
    current.status = RecordStatus.DRAFT
    current.updated_by = restored_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def archive_category(*, organization, category, archived_by=None) -> Category:
    current = _locked_category_for_organization(organization=organization, category=category)
    current.status = RecordStatus.ARCHIVED
    current.updated_by = archived_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_category(*, organization, category, restored_by=None) -> Category:
    current = _locked_category_for_organization(organization=organization, category=category)
    current.status = RecordStatus.DRAFT
    current.updated_by = restored_by
    current.save(update_fields=["status", "updated_by", "updated_at"])
    return current


@transaction.atomic
def archive_offering(*, organization, offering, archived_by=None) -> Offering:
    current = _locked_offering_for_organization(organization=organization, offering=offering)
    current.status = RecordStatus.ARCHIVED
    current.visible_on_website = False
    current.updated_by = archived_by
    current.save(update_fields=["status", "visible_on_website", "updated_by", "updated_at"])
    return current


@transaction.atomic
def restore_offering(*, organization, offering, restored_by=None) -> Offering:
    current = _locked_offering_for_organization(organization=organization, offering=offering)
    current.status = RecordStatus.DRAFT
    current.visible_on_website = False
    current.updated_by = restored_by
    current.save(update_fields=["status", "visible_on_website", "updated_by", "updated_at"])
    return current


def create_product(
    *,
    organization,
    name: str,
    code: str,
    base_price,
    currency: str,
    category=None,
    created_by=None,
) -> Offering:
    return create_offering(
        organization=organization,
        name=name,
        code=code,
        base_price=base_price,
        currency=currency,
        category=category,
        created_by=created_by,
    )


def _clean_offering_payload(
    *,
    name: str,
    code: str,
    base_price,
    currency: str,
    offering_type: str,
    status: str,
) -> dict[str, object]:
    cleaned_name = name.strip()
    cleaned_code = code.strip().upper()
    cleaned_currency = currency.strip().upper()
    cleaned_price = Decimal(base_price)
    if not cleaned_name:
        raise ValueError("Offering name is required.")
    if not cleaned_code:
        raise ValueError("Offering code is required.")
    if len(cleaned_currency) != 3:
        raise ValueError("Currency must use a three-letter ISO code.")
    if cleaned_price < Decimal("0.00"):
        raise ValueError("Base price cannot be negative.")
    if status not in {choice.value for choice in RecordStatus}:
        raise ValueError("Unsupported offering status.")
    if offering_type not in {choice.value for choice in Offering.OfferingType}:
        raise ValueError("Unsupported offering type.")
    return {
        "name": cleaned_name,
        "code": cleaned_code,
        "base_price": cleaned_price,
        "currency": cleaned_currency,
        "offering_type": offering_type,
        "status": status,
    }


def _clean_category_payload(
    *,
    organization,
    name: str,
    slug: str,
    sort_order: int,
    status: str,
    exclude=None,
) -> dict[str, object]:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Category name is required.")
    try:
        cleaned_sort_order = int(sort_order)
    except (TypeError, ValueError) as exc:
        raise ValueError("Sort order must be a number.") from exc
    if cleaned_sort_order < 0:
        raise ValueError("Sort order cannot be negative.")
    if status not in {RecordStatus.ACTIVE, RecordStatus.DRAFT}:
        raise ValueError("Unsupported category status.")

    explicit_slug = bool(slug.strip())
    cleaned_slug = slugify(slug.strip()) if explicit_slug else _unique_category_slug(
        organization=organization,
        name=cleaned_name,
        exclude=exclude,
    )
    if not cleaned_slug:
        raise ValueError("Category slug is required.")
    conflicts = Category.objects.filter(organization=organization, slug__iexact=cleaned_slug)
    if exclude is not None:
        conflicts = conflicts.exclude(id=exclude.id)
    if conflicts.exists():
        raise ValueError("A category with this slug already exists.")
    return {
        "name": cleaned_name,
        "slug": cleaned_slug,
        "sort_order": cleaned_sort_order,
        "status": status,
    }


def _clean_collection_payload(
    *,
    organization,
    name: str,
    slug: str,
    status: str,
    exclude=None,
) -> dict[str, object]:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Collection name is required.")
    if status not in {RecordStatus.ACTIVE, RecordStatus.DRAFT}:
        raise ValueError("Unsupported collection status.")

    explicit_slug = bool(slug.strip())
    cleaned_slug = slugify(slug.strip()) if explicit_slug else _unique_collection_slug(
        organization=organization,
        name=cleaned_name,
        exclude=exclude,
    )
    if not cleaned_slug:
        raise ValueError("Collection slug is required.")
    conflicts = Collection.objects.filter(organization=organization, slug__iexact=cleaned_slug)
    if exclude is not None:
        conflicts = conflicts.exclude(id=exclude.id)
    if conflicts.exists():
        raise ValueError("A collection with this slug already exists.")
    return {
        "name": cleaned_name,
        "slug": cleaned_slug,
        "status": status,
    }


def _clean_option_payload(
    *,
    organization,
    name: str,
    code: str,
    sort_order: int,
    status: str,
    exclude=None,
) -> dict[str, object]:
    cleaned_name = name.strip()
    cleaned_code = code.strip().lower()
    if not cleaned_name:
        raise ValueError("Option name is required.")
    if not cleaned_code:
        raise ValueError("Option code is required.")
    try:
        cleaned_sort_order = int(sort_order)
    except (TypeError, ValueError) as exc:
        raise ValueError("Sort order must be a number.") from exc
    if cleaned_sort_order < 0:
        raise ValueError("Sort order cannot be negative.")
    if status not in {RecordStatus.ACTIVE, RecordStatus.DRAFT}:
        raise ValueError("Unsupported option status.")
    conflicts = OptionDefinition.objects.filter(
        organization=organization,
        code__iexact=cleaned_code,
    )
    if exclude is not None:
        conflicts = conflicts.exclude(id=exclude.id)
    if conflicts.exists():
        raise ValueError("An option with this code already exists.")
    return {
        "name": cleaned_name,
        "code": cleaned_code,
        "sort_order": cleaned_sort_order,
        "status": status,
    }


def _clean_option_value_payload(
    *,
    organization,
    option_definition,
    label: str,
    value: str,
    color_hex: str,
    sort_order: int,
    status: str,
    exclude=None,
) -> dict[str, object]:
    cleaned_label = label.strip()
    cleaned_value = value.strip().lower()
    cleaned_color = color_hex.strip().upper()
    if not cleaned_label:
        raise ValueError("Option value label is required.")
    if not cleaned_value:
        raise ValueError("Option value code is required.")
    try:
        cleaned_sort_order = int(sort_order)
    except (TypeError, ValueError) as exc:
        raise ValueError("Sort order must be a number.") from exc
    if cleaned_sort_order < 0:
        raise ValueError("Sort order cannot be negative.")
    if status not in {RecordStatus.ACTIVE, RecordStatus.DRAFT}:
        raise ValueError("Unsupported option value status.")
    conflicts = OptionValue.objects.filter(
        organization=organization,
        option=option_definition,
        value__iexact=cleaned_value,
    )
    if exclude is not None:
        conflicts = conflicts.exclude(id=exclude.id)
    if conflicts.exists():
        raise ValueError("This option already has that value.")
    return {
        "label": cleaned_label,
        "value": cleaned_value,
        "color_hex": cleaned_color,
        "sort_order": cleaned_sort_order,
        "status": status,
    }


def _clean_variant_payload(
    *,
    organization,
    sku: str,
    title: str,
    price_override,
    stock_tracking_enabled: bool,
    status: str,
    exclude=None,
) -> dict[str, object]:
    cleaned_sku = sku.strip().upper()
    cleaned_title = title.strip()
    if not cleaned_sku:
        raise ValueError("Variant SKU is required.")
    if status not in {RecordStatus.ACTIVE, RecordStatus.DRAFT}:
        raise ValueError("Unsupported variant status.")
    cleaned_price = Decimal(price_override) if price_override not in {None, ""} else None
    if cleaned_price is not None and cleaned_price < Decimal("0.00"):
        raise ValueError("Variant price override cannot be negative.")
    conflicts = OfferingVariant.objects.filter(
        organization=organization,
        sku__iexact=cleaned_sku,
    )
    if exclude is not None:
        conflicts = conflicts.exclude(id=exclude.id)
    if conflicts.exists():
        raise ValueError("A variant with this SKU already exists.")
    return {
        "sku": cleaned_sku,
        "title": cleaned_title,
        "price_override": cleaned_price,
        "stock_tracking_enabled": bool(stock_tracking_enabled),
        "status": status,
    }


def _validate_category_scope(*, organization, facility, category) -> None:
    if category is None:
        return
    if category.organization_id != organization.id:
        raise PermissionDenied("Category does not belong to this organization.")
    if facility is not None and category.facility_id not in {None, facility.id}:
        raise PermissionDenied("Category does not belong to this facility.")
    if category.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
        raise ValueError("Archived categories cannot be assigned to offerings.")


def _validate_category_parent(*, organization, facility, parent, category=None) -> None:
    if parent is None:
        return
    if parent.organization_id != organization.id:
        raise PermissionDenied("Parent category does not belong to this organization.")
    if facility is not None and parent.facility_id not in {None, facility.id}:
        raise PermissionDenied("Parent category does not belong to this facility.")
    if parent.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
        raise ValueError("Archived categories cannot be used as parents.")
    if category is not None:
        if parent.id == category.id:
            raise ValueError("A category cannot be its own parent.")
        if parent.id in _category_descendant_ids(category):
            raise ValueError("A category cannot be moved under one of its descendants.")


def _validate_collection_offerings(*, organization, facility, offerings) -> None:
    seen_ids = set()
    for offering in offerings:
        if offering.id in seen_ids:
            continue
        seen_ids.add(offering.id)
        if offering.organization_id != organization.id:
            raise PermissionDenied("Collection offering does not belong to this organization.")
        if facility is not None and offering.facility_id not in {None, facility.id}:
            raise PermissionDenied("Collection offering does not belong to this facility.")
        if offering.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
            raise ValueError("Archived offerings cannot be assigned to collections.")


def _validate_option_definition_scope(*, organization, facility, option_definition) -> None:
    if option_definition.organization_id != organization.id:
        raise PermissionDenied("Option does not belong to this organization.")
    if facility is not None and option_definition.facility_id not in {None, facility.id}:
        raise PermissionDenied("Option does not belong to this facility.")
    if option_definition.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
        raise ValueError("Archived options cannot be used for active variant workflows.")


def _validate_variant_option_values(*, organization, facility, option_values) -> list:
    selected_values = []
    seen_value_ids = set()
    seen_option_ids = set()
    for option_value in option_values:
        if option_value.id in seen_value_ids:
            continue
        seen_value_ids.add(option_value.id)
        if option_value.organization_id != organization.id:
            raise PermissionDenied("Option value does not belong to this organization.")
        if facility is not None and option_value.facility_id not in {None, facility.id}:
            raise PermissionDenied("Option value does not belong to this facility.")
        option = option_value.option
        if option.organization_id != organization.id:
            raise PermissionDenied("Option does not belong to this organization.")
        if facility is not None and option.facility_id not in {None, facility.id}:
            raise PermissionDenied("Option does not belong to this facility.")
        if option.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
            raise ValueError("Archived options cannot be assigned to variants.")
        if option_value.status in {RecordStatus.ARCHIVED, RecordStatus.DELETED}:
            raise ValueError("Archived option values cannot be assigned to variants.")
        if option.id in seen_option_ids:
            raise ValueError("Choose only one value for each option.")
        seen_option_ids.add(option.id)
        selected_values.append(option_value)
    return selected_values


def _locked_offering_for_organization(*, organization, offering) -> Offering:
    if offering.organization_id != organization.id:
        raise PermissionDenied("Offering does not belong to this organization.")
    return Offering.objects.select_for_update().get(organization=organization, id=offering.id)


def _locked_category_for_organization(*, organization, category) -> Category:
    if category.organization_id != organization.id:
        raise PermissionDenied("Category does not belong to this organization.")
    return Category.objects.select_for_update().get(organization=organization, id=category.id)


def _locked_collection_for_organization(*, organization, collection) -> Collection:
    if collection.organization_id != organization.id:
        raise PermissionDenied("Collection does not belong to this organization.")
    return Collection.objects.select_for_update().get(
        organization=organization,
        id=collection.id,
    )


def _locked_option_for_organization(*, organization, option_definition) -> OptionDefinition:
    if option_definition.organization_id != organization.id:
        raise PermissionDenied("Option does not belong to this organization.")
    return OptionDefinition.objects.select_for_update().get(
        organization=organization,
        id=option_definition.id,
    )


def _locked_option_value_for_organization(*, organization, option_value) -> OptionValue:
    if option_value.organization_id != organization.id:
        raise PermissionDenied("Option value does not belong to this organization.")
    return (
        OptionValue.objects.select_for_update()
        .select_related("option")
        .get(organization=organization, id=option_value.id)
    )


def _locked_variant_for_organization(*, organization, variant) -> OfferingVariant:
    if variant.organization_id != organization.id:
        raise PermissionDenied("Variant does not belong to this organization.")
    return (
        OfferingVariant.objects.select_for_update()
        .select_related("offering")
        .get(organization=organization, id=variant.id)
    )


def _default_variant_for_offering(
    offering: Offering,
    *,
    lock: bool = False,
) -> OfferingVariant | None:
    variants = OfferingVariant.objects.filter(
        organization=offering.organization,
        offering=offering,
        is_default=True,
    ).order_by("created_at")
    if lock:
        variants = variants.select_for_update()
    return variants.first()


def _sync_default_variant(
    *,
    organization,
    offering: Offering,
    facility,
    code: str,
    title: str,
    default_variant: OfferingVariant | None,
    user,
) -> OfferingVariant:
    if default_variant is None:
        return OfferingVariant.objects.create(
            organization=organization,
            facility=facility,
            offering=offering,
            sku=code,
            title=title,
            is_default=True,
            created_by=user,
            updated_by=user,
        )
    default_variant.facility = facility
    default_variant.sku = code
    default_variant.title = title
    default_variant.updated_by = user
    default_variant.save(update_fields=["facility", "sku", "title", "updated_by", "updated_at"])
    return default_variant


def _sync_collection_offerings(
    *,
    organization,
    collection: Collection,
    facility,
    offerings,
    user,
) -> None:
    selected_offerings = []
    seen_ids = set()
    for offering in offerings:
        if offering.id in seen_ids:
            continue
        seen_ids.add(offering.id)
        selected_offerings.append(offering)

    CollectionItem.objects.filter(
        organization=organization,
        collection=collection,
    ).exclude(offering_id__in=seen_ids).delete()

    for index, offering in enumerate(selected_offerings, start=1):
        item, created = CollectionItem.objects.get_or_create(
            organization=organization,
            collection=collection,
            offering=offering,
            defaults={
                "facility": facility,
                "sort_order": index,
                "created_by": user,
                "updated_by": user,
            },
        )
        if not created:
            item.facility = facility
            item.sort_order = index
            item.status = RecordStatus.ACTIVE
            item.updated_by = user
            item.save(
                update_fields=[
                    "facility",
                    "sort_order",
                    "status",
                    "updated_by",
                    "updated_at",
                ]
            )


def _unique_offering_slug(*, organization, name: str, code: str, exclude=None) -> str:
    base_slug = slugify(name) or slugify(code) or "offering"
    base_slug = base_slug[:180]
    candidate = base_slug
    counter = 2
    queryset = Offering.objects.filter(organization=organization, slug=candidate)
    if exclude is not None:
        queryset = queryset.exclude(id=exclude.id)
    while queryset.exists():
        suffix = f"-{counter}"
        candidate = f"{base_slug[: 180 - len(suffix)]}{suffix}"
        queryset = Offering.objects.filter(organization=organization, slug=candidate)
        if exclude is not None:
            queryset = queryset.exclude(id=exclude.id)
        counter += 1
    return candidate


def _unique_collection_slug(*, organization, name: str, exclude=None) -> str:
    base_slug = slugify(name) or "collection"
    base_slug = base_slug[:160]
    candidate = base_slug
    counter = 2
    queryset = Collection.objects.filter(organization=organization, slug__iexact=candidate)
    if exclude is not None:
        queryset = queryset.exclude(id=exclude.id)
    while queryset.exists():
        suffix = f"-{counter}"
        candidate = f"{base_slug[: 160 - len(suffix)]}{suffix}"
        queryset = Collection.objects.filter(organization=organization, slug__iexact=candidate)
        if exclude is not None:
            queryset = queryset.exclude(id=exclude.id)
        counter += 1
    return candidate


def _unique_category_slug(*, organization, name: str, exclude=None) -> str:
    base_slug = slugify(name) or "category"
    base_slug = base_slug[:160]
    candidate = base_slug
    counter = 2
    queryset = Category.objects.filter(organization=organization, slug__iexact=candidate)
    if exclude is not None:
        queryset = queryset.exclude(id=exclude.id)
    while queryset.exists():
        suffix = f"-{counter}"
        candidate = f"{base_slug[: 160 - len(suffix)]}{suffix}"
        queryset = Category.objects.filter(organization=organization, slug__iexact=candidate)
        if exclude is not None:
            queryset = queryset.exclude(id=exclude.id)
        counter += 1
    return candidate


def _category_descendant_ids(category: Category) -> set:
    descendants = set()
    frontier = [category.id]
    while frontier:
        child_ids = list(
            Category.objects.filter(
                organization=category.organization,
                parent_id__in=frontier,
            ).values_list("id", flat=True)
        )
        new_child_ids = [child_id for child_id in child_ids if child_id not in descendants]
        descendants.update(new_child_ids)
        frontier = new_child_ids
    return descendants
