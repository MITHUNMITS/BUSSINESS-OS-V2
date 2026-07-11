from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from business_os.apps.inventory.models import InventoryItem, InventoryLevel, InventoryReservation, StockMovement


class InsufficientStockError(ValueError):
    """Raised when a checkout or hold would exceed sellable stock."""


@transaction.atomic
def reserve_stock(
    *,
    organization,
    facility,
    variant,
    quantity: int,
    idempotency_key: str,
    minutes: int = 20,
) -> InventoryReservation:
    item = InventoryItem.objects.select_for_update().get(organization=organization, variant=variant)
    level = InventoryLevel.objects.select_for_update().get(
        organization=organization,
        facility=facility,
        item=item,
    )
    existing = InventoryReservation.objects.filter(
        organization=organization,
        item=item,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        return existing

    if level.available < quantity:
        raise InsufficientStockError(f"Only {level.available} units are available for {item.sku}.")

    level.reserved += quantity
    level.save(update_fields=["reserved", "updated_at"])
    reservation = InventoryReservation.objects.create(
        organization=organization,
        facility=facility,
        item=item,
        quantity=quantity,
        idempotency_key=idempotency_key,
        expires_at=timezone.now() + timedelta(minutes=minutes),
    )
    StockMovement.objects.create(
        organization=organization,
        facility=facility,
        item=item,
        movement_type=StockMovement.MovementType.RESERVATION,
        quantity_delta=-quantity,
        reference=str(reservation.id),
    )
    return reservation


@transaction.atomic
def confirm_reservation(*, reservation: InventoryReservation) -> None:
    reservation = InventoryReservation.objects.select_for_update().get(id=reservation.id)
    if reservation.status == InventoryReservation.ReservationStatus.CONFIRMED:
        return
    level = InventoryLevel.objects.select_for_update().get(
        organization=reservation.organization,
        facility=reservation.facility,
        item=reservation.item,
    )
    level.reserved -= reservation.quantity
    level.on_hand -= reservation.quantity
    level.save(update_fields=["reserved", "on_hand", "updated_at"])
    reservation.status = InventoryReservation.ReservationStatus.CONFIRMED
    reservation.confirmed_at = timezone.now()
    reservation.save(update_fields=["status", "confirmed_at", "updated_at"])
    StockMovement.objects.create(
        organization=reservation.organization,
        facility=reservation.facility,
        item=reservation.item,
        movement_type=StockMovement.MovementType.SALE,
        quantity_delta=-reservation.quantity,
        reference=str(reservation.id),
    )
