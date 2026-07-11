from __future__ import annotations

from django.db import models
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TenantOwnedModel


class InventoryItem(TenantOwnedModel):
    variant = models.OneToOneField(
        "catalogue.OfferingVariant",
        on_delete=models.CASCADE,
        related_name="inventory_item",
    )
    sku = models.CharField(max_length=80)
    safety_stock = models.PositiveIntegerField(default=0)
    track_stock = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "sku"], name="unique_inventory_sku_per_org")
        ]

    def __str__(self) -> str:
        return self.sku


class InventoryLevel(TenantOwnedModel):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="levels")
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    safety_stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "facility", "item"], name="unique_inventory_level")
        ]

    @property
    def available(self) -> int:
        return max(self.on_hand - self.reserved - self.safety_stock, 0)


class InventoryReservation(TenantOwnedModel):
    class ReservationStatus(models.TextChoices):
        HELD = "held", _("Held")
        CONFIRMED = "confirmed", _("Confirmed")
        RELEASED = "released", _("Released")
        EXPIRED = "expired", _("Expired")

    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name="reservations")
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=32,
        choices=ReservationStatus.choices,
        default=ReservationStatus.HELD,
        db_index=True,
    )
    idempotency_key = models.CharField(max_length=120, blank=True, db_index=True)
    expires_at = models.DateTimeField(default=lambda: timezone.now() + timedelta(minutes=20))
    confirmed_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "status", "expires_at"])]


class StockMovement(TenantOwnedModel):
    class MovementType(models.TextChoices):
        ADJUSTMENT = "adjustment", _("Adjustment")
        RESERVATION = "reservation", _("Reservation")
        RELEASE = "release", _("Release")
        SALE = "sale", _("Sale")
        RETURN = "return", _("Return")

    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=32, choices=MovementType.choices)
    quantity_delta = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=120, blank=True, db_index=True)
