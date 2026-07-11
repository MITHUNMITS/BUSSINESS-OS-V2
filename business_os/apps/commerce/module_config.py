MODULE_CONFIG = {
    "code": "commerce",
    "name": "Commerce, Orders & POS",
    "description": "Cart, checkout, orders, shipping, returns foundation, and sales channels.",
    "category": "sell",
    "icon": "shopping-cart",
    "capabilities": [
        "commerce.cart",
        "commerce.checkout",
        "commerce.orders",
        "commerce.guest_checkout",
    ],
    "navigation": [
        {"label": "Orders", "url_name": "admin-orders", "icon": "shopping-bag"},
    ],
    "website_contributions": [
        {"type": "page", "slug": "cart", "capability": "commerce.cart"},
        {"type": "page", "slug": "checkout", "capability": "commerce.checkout"},
    ],
}
