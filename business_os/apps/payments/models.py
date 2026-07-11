from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TenantOwnedModel


class PaymentProvider(TenantOwnedModel):
    class ProviderType(models.TextChoices):
        MANUAL = "manual", _("Manual")
        COD = "cod", _("Cash on delivery")
        HOSTED = "hosted", _("Hosted gateway")

    name = models.CharField(max_length=120)
    provider_type = models.CharField(max_length=40, choices=ProviderType.choices)
    active = models.BooleanField(default=True)
    public_config = models.JSONField(default=dict, blank=True)
    secret_reference = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name


class PaymentIntent(TenantOwnedModel):
    class IntentStatus(models.TextChoices):
        REQUIRES_PAYMENT = "requires_payment", _("Requires payment")
        PROCESSING = "processing", _("Processing")
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    provider = models.ForeignKey(
        PaymentProvider, on_delete=models.PROTECT, related_name="payment_intents"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=32,
        choices=IntentStatus.choices,
        default=IntentStatus.REQUIRES_PAYMENT,
        db_index=True,
    )
    idempotency_key = models.CharField(max_length=120, db_index=True)
    external_reference = models.CharField(max_length=160, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "idempotency_key"],
                name="unique_payment_intent_idempotency_key",
            )
        ]


class PaymentTransaction(TenantOwnedModel):
    intent = models.ForeignKey(PaymentIntent, on_delete=models.PROTECT, related_name="transactions")
    provider = models.ForeignKey(
        PaymentProvider, on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=40, db_index=True)
    external_reference = models.CharField(max_length=160, blank=True, db_index=True)
    raw_event_reference = models.CharField(max_length=160, blank=True, db_index=True)
