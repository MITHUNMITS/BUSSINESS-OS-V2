from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from business_os.apps.commerce.models import Cart, CartItem, Order, OrderItem
from business_os.apps.entitlements.services import has_entitlement
from business_os.apps.inventory.services import confirm_reservation, reserve_stock
from business_os.apps.payments.models import PaymentProvider
from business_os.apps.payments.services import create_manual_payment_intent


class EntitlementRequiredError(PermissionDenied):
    """Raised when a commerce action is blocked by organization entitlements."""


def _line_total(unit_price, quantity: int):
    return unit_price * Decimal(quantity)


def _require_capability(organization, capability_code: str) -> None:
    if not has_entitlement(organization=organization, capability_code=capability_code):
        raise EntitlementRequiredError(f"{capability_code} is required.")


def _order_number(organization) -> str:
    prefix = organization.slug.upper().replace("-", "")[:8]
    stamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{uuid4().hex[:6].upper()}"


@transaction.atomic
def get_or_create_cart(*, organization, facility, user=None, session_key: str = "", currency: str = "AED") -> Cart:
    _require_capability(organization, "commerce.cart")
    lookup = {"organization": organization, "status": Cart.CartStatus.OPEN}
    if user and user.is_authenticated:
        lookup["user"] = user
    else:
        lookup["session_key"] = session_key
    cart, _created = Cart.objects.get_or_create(
        **lookup,
        defaults={"facility": facility, "currency": currency},
    )
    return cart


@transaction.atomic
def add_to_cart(*, cart: Cart, variant, quantity: int) -> CartItem:
    _require_capability(cart.organization, "commerce.cart")
    unit_price = variant.price
    item, created = CartItem.objects.get_or_create(
        organization=cart.organization,
        facility=cart.facility,
        cart=cart,
        variant=variant,
        defaults={
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": _line_total(unit_price, quantity),
        },
    )
    if not created:
        item.quantity += quantity
        item.unit_price = unit_price
        item.line_total = _line_total(unit_price, item.quantity)
        item.save(update_fields=["quantity", "unit_price", "line_total", "updated_at"])
    return item


@transaction.atomic
def checkout_cart(
    *,
    cart: Cart,
    customer_email: str,
    customer_phone: str,
    shipping_address: dict,
    payment_provider: PaymentProvider,
    idempotency_key: str,
) -> Order:
    _require_capability(cart.organization, "commerce.checkout")
    if not cart.user_id:
        _require_capability(cart.organization, "commerce.guest_checkout")
    existing = Order.objects.filter(
        organization=cart.organization,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        return existing

    locked_cart = Cart.objects.select_for_update().get(id=cart.id)
    cart_items = list(locked_cart.items.select_related("variant__offering"))
    subtotal = sum((item.line_total for item in cart_items), Decimal("0.00"))
    shipping_total = Decimal("0.00")
    tax_total = Decimal("0.00")
    grand_total = subtotal + shipping_total + tax_total
    payment_intent = create_manual_payment_intent(
        organization=locked_cart.organization,
        provider=payment_provider,
        amount=grand_total,
        currency=locked_cart.currency,
        idempotency_key=f"payment:{idempotency_key}",
        metadata={"cart_id": str(locked_cart.id)},
    )
    order = Order.objects.create(
        organization=locked_cart.organization,
        facility=locked_cart.facility,
        order_number=_order_number(locked_cart.organization),
        cart=locked_cart,
        user=locked_cart.user,
        customer_email=customer_email,
        customer_phone=customer_phone,
        shipping_address=shipping_address,
        billing_address=shipping_address,
        currency=locked_cart.currency,
        subtotal=subtotal,
        shipping_total=shipping_total,
        tax_total=tax_total,
        grand_total=grand_total,
        order_status=Order.OrderStatus.CONFIRMED
        if payment_intent.status == "succeeded"
        else Order.OrderStatus.PENDING_PAYMENT,
        idempotency_key=idempotency_key,
        payment_intent=payment_intent,
        created_by=locked_cart.user,
    )
    for item in cart_items:
        reservation = reserve_stock(
            organization=locked_cart.organization,
            facility=locked_cart.facility,
            variant=item.variant,
            quantity=item.quantity,
            idempotency_key=f"order:{order.id}:variant:{item.variant_id}",
        )
        if payment_intent.status == "succeeded":
            confirm_reservation(reservation=reservation)
        OrderItem.objects.create(
            organization=locked_cart.organization,
            facility=locked_cart.facility,
            order=order,
            variant=item.variant,
            product_name=item.variant.offering.name,
            sku=item.variant.sku,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
            reservation=reservation,
        )
    locked_cart.status = Cart.CartStatus.ORDERED
    locked_cart.customer_email = customer_email
    locked_cart.save(update_fields=["status", "customer_email", "updated_at"])
    return order
