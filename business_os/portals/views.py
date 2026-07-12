from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.commerce.models import Order
from business_os.apps.core.models import PlatformPermission, SupportAccessScope
from business_os.apps.core.module_registry import get_navigation, load_module_definitions
from business_os.apps.core.services import (
    end_support_session,
    has_platform_permission,
    record_support_access,
    require_platform_permission,
    require_support_access,
    start_support_session,
)
from business_os.apps.marketplace.selectors import visible_marketplace_modules
from business_os.apps.organizations.models import Membership, Organization
from business_os.apps.websites.services import visible_pages_for_website


def _organization_context(request, organization_slug: str):
    organization = get_object_or_404(Organization, slug=organization_slug)
    user = request.user
    is_member = user.is_authenticated and (
        Membership.objects.filter(
            organization=organization,
            user=user,
            membership_status="active",
        ).exists()
    )
    if not is_member:
        raise PermissionDenied("Organization membership is required.")
    navigation = get_navigation(organization=organization, user=request.user)
    return organization, navigation


def _require_platform_portal_access(request) -> None:
    require_platform_permission(request.user, PlatformPermission.PORTAL_ACCESS)


def _support_session_for_organization(request, organization: Organization):
    support_session = getattr(request, "support_session", None)
    if support_session is None or support_session.organization_id != organization.id:
        return None
    require_support_access(
        support_session=support_session,
        organization=organization,
        action="view",
    )
    record_support_access(request=request, support_session=support_session)
    return support_session


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
    _require_platform_portal_access(request)
    modules = load_module_definitions()
    organizations = (
        Organization.objects.order_by("name")[:10]
        if has_platform_permission(request.user, PlatformPermission.ORGANIZATIONS_VIEW)
        else []
    )
    return render(
        request,
        "platform_portal/overview.html",
        {"modules": modules.values(), "organizations": organizations},
    )


def platform_modules(request):
    _require_platform_portal_access(request)
    modules = load_module_definitions()
    return render(request, "platform_portal/modules.html", {"modules": modules.values()})


def platform_organizations(request):
    _require_platform_portal_access(request)
    require_platform_permission(request.user, PlatformPermission.ORGANIZATIONS_VIEW)
    organizations = Organization.objects.order_by("name")
    return render(
        request,
        "platform_portal/organizations.html",
        {"organizations": organizations},
    )


def platform_organization_workspace(request, organization_slug: str):
    _require_platform_portal_access(request)
    organization = get_object_or_404(Organization, slug=organization_slug)
    support_session = _support_session_for_organization(request, organization)
    if support_session is None:
        require_platform_permission(request.user, PlatformPermission.ORGANIZATIONS_VIEW)
    return render(
        request,
        "platform_portal/organization_workspace.html",
        {"organization": organization, "support_session": support_session},
    )


def platform_start_support_session(request, organization_slug: str):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    _require_platform_portal_access(request)
    organization = get_object_or_404(Organization, slug=organization_slug)
    try:
        duration_minutes = int(request.POST.get("duration_minutes", "60"))
    except ValueError:
        return HttpResponseBadRequest("duration_minutes must be a number.")
    if duration_minutes < 1 or duration_minutes > 480:
        return HttpResponseBadRequest("duration_minutes must be between 1 and 480.")

    try:
        start_support_session(
            actor=request.user,
            organization=organization,
            reason=request.POST.get("reason", ""),
            scope=SupportAccessScope.READ_ONLY,
            ticket_reference=request.POST.get("ticket_reference", ""),
            expires_at=timezone.now() + timedelta(minutes=duration_minutes),
            request=request,
        )
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    return redirect(f"/organizations/{organization.slug}/")


def platform_end_support_session(request, organization_slug: str):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    _require_platform_portal_access(request)
    organization = get_object_or_404(Organization, slug=organization_slug)
    support_session = _support_session_for_organization(request, organization)
    if support_session is None:
        raise PermissionDenied("An active support session is required.")
    end_support_session(
        actor=request.user,
        support_session=support_session,
        request=request,
    )
    return redirect("/organizations/")
