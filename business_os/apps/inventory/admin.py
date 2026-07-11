from django.contrib import admin

from business_os.apps.inventory.models import (
    InventoryItem,
    InventoryLevel,
    InventoryReservation,
    StockMovement,
)

admin.site.register(InventoryItem)
admin.site.register(InventoryLevel)
admin.site.register(InventoryReservation)
admin.site.register(StockMovement)
