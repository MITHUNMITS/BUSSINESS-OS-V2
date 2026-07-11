from django.contrib import admin

from business_os.apps.commerce.models import Cart, CartItem, Order, OrderItem, ShippingRule, ShippingZone

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingZone)
admin.site.register(ShippingRule)

