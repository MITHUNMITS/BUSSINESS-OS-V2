from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TenantOwnedModel


class SubscriptionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    PAST_DUE = "past_due", _("Past due")
    GRACE_PERIOD = "grace_period", _("Grace period")
    SUSPENDED = "suspended", _("Suspended")
    CANCEL_AT_PERIOD_END = "cancel_at_period_end", _("Cancel at period end")
    CANCELLED = "cancelled", _("Cancelled")
    EXPIRED = "expired", _("Expired")


class OrganizationSubscription(TenantOwnedModel):
    status = models.CharField(
        max_length=40,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.DRAFT,
        db_index=True,
    )
    currency = models.CharField(max_length=3)
    billing_period = models.CharField(max_length=20, default="monthly")
    starts_at = models.DateTimeField(null=True, blank=True)
    renews_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    price_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "status", "renews_at"])]


class SubscriptionItem(TenantOwnedModel):
    subscription = models.ForeignKey(
        OrganizationSubscription,
        on_delete=models.CASCADE,
        related_name="items",
    )
    module = models.ForeignKey(
        "marketplace.Module", on_delete=models.PROTECT, related_name="subscription_items"
    )
    capability = models.ForeignKey(
        "marketplace.Capability",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subscription_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "subscription"])]


class PlatformBillingInvoice(TenantOwnedModel):
    class InvoiceStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ISSUED = "issued", _("Issued")
        PARTIALLY_PAID = "partially_paid", _("Partially paid")
        PAID = "paid", _("Paid")
        VOID = "void", _("Void")
        OVERDUE = "overdue", _("Overdue")

    invoice_number = models.CharField(max_length=80, unique=True)
    subscription = models.ForeignKey(
        OrganizationSubscription,
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    status = models.CharField(
        max_length=32,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        db_index=True,
    )
    currency = models.CharField(max_length=3)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    calculation_snapshot = models.JSONField(default=dict, blank=True)


class PlatformBillingInvoiceLine(TenantOwnedModel):
    invoice = models.ForeignKey(
        PlatformBillingInvoice, on_delete=models.CASCADE, related_name="lines"
    )
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    snapshot = models.JSONField(default=dict, blank=True)


class PlatformBillingPayment(TenantOwnedModel):
    invoice = models.ForeignKey(
        PlatformBillingInvoice, on_delete=models.PROTECT, related_name="payments"
    )
    provider = models.CharField(max_length=80)
    external_reference = models.CharField(max_length=160, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=40, default="pending", db_index=True)
    idempotency_key = models.CharField(max_length=120, blank=True, db_index=True)
