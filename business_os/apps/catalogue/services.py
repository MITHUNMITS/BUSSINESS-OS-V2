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

    name = name.strip()
    code = code.strip().upper()
    currency = currency.strip().upper()
    if not name:
        raise ValueError("Offering name is required.")
    if not code:
        raise ValueError("Offering code is required.")
    if len(currency) != 3:
        raise ValueError("Currency must use a three-letter ISO code.")
    if Decimal(base_price) < Decimal("0.00"):
        raise ValueError("Base price cannot be negative.")
    if status not in {choice.value for choice in RecordStatus}:
        raise ValueError("Unsupported offering status.")
    if offering_type not in {choice.value for choice in Offering.OfferingType}:
        raise ValueError("Unsupported offering type.")
    if Offering.objects.filter(organization=organization, code__iexact=code).exists():
        raise ValueError("An offering with this code already exists.")
    if OfferingVariant.objects.filter(organization=organization, sku__iexact=code).exists():
        raise ValueError("A variant with this SKU already exists.")

    product = Offering.objects.create(
        organization=organization,
        facility=facility,
        category=category,
        offering_type=offering_type,
        name=name,
        slug=_unique_offering_slug(organization=organization, name=name, code=code),
        code=code,
        summary=summary.strip(),
        description=description.strip(),
        base_price=base_price,
        currency=currency,
        visible_on_website=visible_on_website,
        whatsapp_inquiry_enabled=whatsapp_inquiry_enabled,
        status=status,
        created_by=created_by,
    )
    OfferingVariant.objects.create(
        organization=organization,
        facility=facility,
        offering=product,
        sku=code,
        title=name,
        is_default=True,
        created_by=created_by,
    )
    return product


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


def _unique_offering_slug(*, organization, name: str, code: str) -> str:
    base_slug = slugify(name) or slugify(code) or "offering"
    base_slug = base_slug[:180]
    candidate = base_slug
    counter = 2
    while Offering.objects.filter(organization=organization, slug=candidate).exists():
        suffix = f"-{counter}"
        candidate = f"{base_slug[: 180 - len(suffix)]}{suffix}"
        counter += 1
    return candidate
