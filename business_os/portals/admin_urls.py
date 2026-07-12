from django.urls import path

from business_os.portals import views

urlpatterns = [
    path("o/<slug:organization_slug>/dashboard/", views.admin_dashboard, name="admin-dashboard"),
    path(
        "o/<slug:organization_slug>/marketplace/", views.admin_marketplace, name="admin-marketplace"
    ),
    path("o/<slug:organization_slug>/billing/", views.admin_billing, name="admin-billing"),
    path("o/<slug:organization_slug>/website/", views.admin_website, name="admin-website"),
    path("o/<slug:organization_slug>/products/", views.admin_products, name="admin-products"),
    path(
        "o/<slug:organization_slug>/products/new/",
        views.admin_product_create,
        name="admin-products-create",
    ),
    path(
        "o/<slug:organization_slug>/products/<uuid:offering_id>/",
        views.admin_product_detail,
        name="admin-products-detail",
    ),
    path(
        "o/<slug:organization_slug>/products/<uuid:offering_id>/edit/",
        views.admin_product_edit,
        name="admin-products-edit",
    ),
    path(
        "o/<slug:organization_slug>/products/<uuid:offering_id>/archive/",
        views.admin_product_archive,
        name="admin-products-archive",
    ),
    path(
        "o/<slug:organization_slug>/products/<uuid:offering_id>/restore/",
        views.admin_product_restore,
        name="admin-products-restore",
    ),
    path("o/<slug:organization_slug>/categories/", views.admin_categories, name="admin-categories"),
    path(
        "o/<slug:organization_slug>/categories/new/",
        views.admin_category_create,
        name="admin-categories-create",
    ),
    path(
        "o/<slug:organization_slug>/categories/<uuid:category_id>/",
        views.admin_category_detail,
        name="admin-categories-detail",
    ),
    path(
        "o/<slug:organization_slug>/categories/<uuid:category_id>/edit/",
        views.admin_category_edit,
        name="admin-categories-edit",
    ),
    path(
        "o/<slug:organization_slug>/categories/<uuid:category_id>/archive/",
        views.admin_category_archive,
        name="admin-categories-archive",
    ),
    path(
        "o/<slug:organization_slug>/categories/<uuid:category_id>/restore/",
        views.admin_category_restore,
        name="admin-categories-restore",
    ),
    path("o/<slug:organization_slug>/inventory/", views.admin_inventory, name="admin-inventory"),
    path("o/<slug:organization_slug>/orders/", views.admin_orders, name="admin-orders"),
    path("o/<slug:organization_slug>/payments/", views.admin_payments, name="admin-payments"),
    path("o/<slug:organization_slug>/analytics/", views.admin_analytics, name="admin-analytics"),
    path("o/<slug:organization_slug>/settings/", views.admin_settings, name="admin-settings"),
]
