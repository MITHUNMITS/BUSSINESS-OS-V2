from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.commerce.models import Order
from business_os.apps.core.module_registry import get_navigation, load_module_definitions
from business_os.apps.marketplace.selectors import visible_marketplace_modules
from business_os.apps.organizations.models import Membership, Organization
from business_os.apps.websites.services import visible_pages_for_website


def _organization_context(request, organization_slug: str):
    organization = get_object_or_404(Organization, slug=organization_slug)
    user = request.user
    is_member = user.is_authenticated and (
        getattr(user, "is_platform_staff", False)
        or Membership.objects.filter(
            organization=organization,
            user=user,
            membership_status="active",
        ).exists()
    )
    if not is_member:
        raise PermissionDenied("Organization membership is required.")
    navigation = get_navigation(organization=organization, user=request.user)
    return organization, navigation


def _require_platform_staff(request):
    if not (
        request.user.is_authenticated
        and getattr(request.user, "is_platform_staff", False)
    ):
        raise PermissionDenied("Platform staff access is required.")


def admin_dashboard(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    products = visible_offerings_for_organization(organization)[:5]
    recent_orders = Order.objects.for_organization(organization).order_by("-created_at")[:5]
    return render(
        request,
        "admin_portal/dashboard.html",
        {
            "organization": organization,
            "navigation": navigation,
            "products": products,
            "recent_orders": recent_orders,
        },
    )


def admin_marketplace(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    modules = visible_marketplace_modules(country=organization.country)
    return render(
        request,
        "admin_portal/marketplace.html",
        {"organization": organization, "navigation": navigation, "modules": modules},
    )


def admin_billing(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Billing", "organization": organization, "navigation": navigation},
    )


def admin_website(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    pages = (
        visible_pages_for_website(website=organization.website)
        if hasattr(organization, "website")
        else []
    )
    return render(
        request,
        "admin_portal/website.html",
        {"organization": organization, "navigation": navigation, "pages": pages},
    )


def admin_products(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    products = visible_offerings_for_organization(organization)
    return render(
        request,
        "admin_portal/products.html",
        {"organization": organization, "navigation": navigation, "products": products},
    )


def admin_categories(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Categories", "organization": organization, "navigation": navigation},
    )


def admin_inventory(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Inventory", "organization": organization, "navigation": navigation},
    )


def admin_orders(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    orders = Order.objects.for_organization(organization).order_by("-created_at")
    return render(
        request,
        "admin_portal/orders.html",
        {"organization": organization, "navigation": navigation, "orders": orders},
    )


def admin_payments(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Payments", "organization": organization, "navigation": navigation},
    )


def admin_analytics(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Analytics", "organization": organization, "navigation": navigation},
    )


def admin_settings(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        {"title": "Settings", "organization": organization, "navigation": navigation},
    )


def platform_overview(request):
    _require_platform_staff(request)
    modules = load_module_definitions()
    organizations = Organization.objects.order_by("name")[:10]
    return render(
        request,
        "platform_portal/overview.html",
        {"modules": modules.values(), "organizations": organizations},
    )


def platform_modules(request):
    _require_platform_staff(request)
    modules = load_module_definitions()
    return render(request, "platform_portal/modules.html", {"modules": modules.values()})


def platform_organizations(request):
    _require_platform_staff(request)
    organizations = Organization.objects.order_by("name")
    return render(request, "platform_portal/organizations.html", {"organizations": organizations})
