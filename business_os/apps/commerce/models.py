from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TenantOwnedModel


class Cart(TenantOwnedModel):
    class CartStatus(models.TextChoices):
        OPEN = "open", _("Open")
        ORDERED = "ordered", _("Ordered")
        ABANDONED = "abandoned", _("Abandoned")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    customer_email = models.EmailField(blank=True)
    currency = models.CharField(max_length=3, default="AED")
    status = models.CharField(
        max_length=32, choices=CartStatus.choices, default=CartStatus.OPEN, db_index=True
    )

    class Meta:
        indexes = [models.Index(fields=["organization", "session_key", "status"])]


class CartItem(TenantOwnedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalogue.OfferingVariant", on_delete=models.PROTECT, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "cart", "variant"], name="unique_cart_variant"
            )
        ]


class ShippingZone(TenantOwnedModel):
    name = models.CharField(max_length=120)
    countries = models.JSONField(default=list, blank=True)
    regions = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)


class ShippingRule(TenantOwnedModel):
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=120)
    flat_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    free_over_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3)
    active = models.BooleanField(default=True)


class Order(TenantOwnedModel):
    class OrderStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PENDING_PAYMENT = "pending_payment", _("Pending payment")
        PAID = "paid", _("Paid")
        CONFIRMED = "confirmed", _("Confirmed")
        PROCESSING = "processing", _("Processing")
        FULFILLED = "fulfilled", _("Fulfilled")
        DELIVERED = "delivered", _("Delivered")
        CANCELLED = "cancelled", _("Cancelled")
        REFUNDED = "refunded", _("Refunded")

    order_number = models.CharField(max_length=80, unique=True)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT, related_name="order")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=40, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    currency = models.CharField(max_length=3)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_status = models.CharField(
        max_length=40,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT,
        db_index=True,
    )
    idempotency_key = models.CharField(max_length=120, db_index=True)
    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    class Meta:
        indexes = [models.Index(fields=["organization", "order_status", "created_at"])]


class OrderItem(TenantOwnedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalogue.OfferingVariant", on_delete=models.PROTECT, related_name="order_items"
    )
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    reservation = models.ForeignKey(
        "inventory.InventoryReservation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
