from decimal import Decimal

import pytest

from business_os.apps.catalogue.services import create_product
from business_os.apps.commerce.services import add_to_cart, checkout_cart, get_or_create_cart
from business_os.apps.entitlements.services import grant_entitlement
from business_os.apps.inventory.models import InventoryItem, InventoryLevel
from business_os.apps.organizations.models import Facility, Organization
from business_os.apps.payments.models import PaymentProvider


@pytest.mark.django_db
def test_guest_checkout_reserves_and_confirms_stock():
    organization = Organization.objects.create(
        slug="nova",
        name="Nova",
        default_currency="AED",
        timezone="Asia/Dubai",
    )
    facility = Facility.objects.create(
        organization=organization,
        name="Online Store",
        code="online",
        currency="AED",
        timezone="Asia/Dubai",
    )
    provider = PaymentProvider.objects.create(
        organization=organization,
        facility=facility,
        name="Cash on delivery",
        provider_type=PaymentProvider.ProviderType.COD,
    )
    grant_entitlement(organization=organization, code="commerce.cart")
    grant_entitlement(organization=organization, code="commerce.checkout")
    grant_entitlement(organization=organization, code="commerce.guest_checkout")
    product = create_product(
        organization=organization,
        name="Linen Wrap Dress",
        code="NOVA-001",
        base_price=Decimal("299.00"),
        currency="AED",
    )
    variant = product.variants.get()
    item = InventoryItem.objects.create(
        organization=organization,
        facility=facility,
        variant=variant,
        sku=variant.sku,
    )
    InventoryLevel.objects.create(
        organization=organization,
        facility=facility,
        item=item,
        on_hand=3,
    )
    cart = get_or_create_cart(
        organization=organization,
        facility=facility,
        session_key="guest-session",
        currency="AED",
    )
    add_to_cart(cart=cart, variant=variant, quantity=2)

    order = checkout_cart(
        cart=cart,
        customer_email="customer@example.com",
        customer_phone="+971500000000",
        shipping_address={"country": "AE", "city": "Dubai"},
        payment_provider=provider,
        idempotency_key="checkout-1",
    )

    level = InventoryLevel.objects.get(item=item)
    assert order.grand_total == Decimal("598.00")
    assert order.order_status == "confirmed"
    assert level.on_hand == 1
    assert level.reserved == 0
