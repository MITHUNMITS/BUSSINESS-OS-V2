from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify

from business_os.apps.catalogue.models import Offering, OfferingVariant


@transaction.atomic
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
    product = Offering.objects.create(
        organization=organization,
        category=category,
        name=name,
        slug=slugify(name),
        code=code,
        base_price=base_price,
        currency=currency,
        status="active",
        created_by=created_by,
    )
    OfferingVariant.objects.create(
        organization=organization,
        offering=product,
        sku=code,
        is_default=True,
        created_by=created_by,
    )
    return product
