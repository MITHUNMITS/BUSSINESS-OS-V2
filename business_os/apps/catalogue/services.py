from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.text import slugify

from business_os.apps.catalogue.models import Offering, OfferingVariant
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


def _locked_offering_for_organization(*, organization, offering) -> Offering:
    if offering.organization_id != organization.id:
        raise PermissionDenied("Offering does not belong to this organization.")
    return Offering.objects.select_for_update().get(organization=organization, id=offering.id)


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
