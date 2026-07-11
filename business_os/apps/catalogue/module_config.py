MODULE_CONFIG = {
    "code": "catalogue",
    "name": "Catalogue & Offerings",
    "description": "Products, categories, collections, variants, prices, images, and inquiries.",
    "category": "sell",
    "icon": "package",
    "capabilities": [
        "catalogue.basic",
        "catalogue.variants",
        "catalogue.collections",
        "catalogue.whatsapp_inquiry",
    ],
    "navigation": [
        {"label": "Products", "url_name": "admin-products", "icon": "package"},
        {"label": "Categories", "url_name": "admin-categories", "icon": "tags"},
    ],
    "website_contributions": [
        {"type": "page", "slug": "shop", "capability": "catalogue.basic"},
        {"type": "section", "section_type": "product_grid", "capability": "catalogue.basic"},
    ],
}

