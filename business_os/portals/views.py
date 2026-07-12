from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from business_os.apps.catalogue.forms import CategoryAdminForm, OfferingAdminForm
from business_os.apps.catalogue.selectors import (
    admin_categories_for_organization,
    admin_category_for_organization,
    admin_offering_for_organization,
    admin_offerings_for_organization,
    visible_offerings_for_organization,
)
from business_os.apps.catalogue.services import (
    archive_category,
    archive_offering,
    create_category,
    create_offering,
    restore_category,
    restore_offering,
    update_category,
    update_offering,
)
from business_os.apps.commerce.models import Order
from business_os.apps.core.models import PlatformPermission, RecordStatus, SupportAccessScope
from business_os.apps.core.module_registry import get_navigation, load_module_definitions
from business_os.apps.core.services import (
    AuditTarget,
    audit_event,
    end_support_session,
    has_platform_permission,
    record_support_access,
    require_platform_permission,
    require_support_access,
    start_support_session,
)
from business_os.apps.marketplace.selectors import visible_marketplace_modules
from business_os.apps.organizations.facility_profiles import (
    page_title_for_url_name,
    resolve_facility_profile,
)
from business_os.apps.organizations.models import Membership, Organization
from business_os.apps.websites.services import visible_pages_for_website


def _organization_context(request, organization_slug: str):
    organization = get_object_or_404(Organization, slug=organization_slug)
    request.organization = organization
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
    facility_profile = resolve_facility_profile(organization=organization)
    request.facility = facility_profile.facility
    request.facility_profile = facility_profile
    navigation = get_navigation(
        organization=organization,
        user=request.user,
        facility=facility_profile.facility,
    )
    return organization, navigation


def _admin_urls(organization):
    base = f"/o/{organization.slug}"
    return {
        "dashboard": f"{base}/dashboard/",
        "marketplace": f"{base}/marketplace/",
        "billing": f"{base}/billing/",
        "website": f"{base}/website/",
        "products": f"{base}/products/",
        "products_create": f"{base}/products/new/",
        "categories": f"{base}/categories/",
        "categories_create": f"{base}/categories/new/",
        "inventory": f"{base}/inventory/",
        "orders": f"{base}/orders/",
        "payments": f"{base}/payments/",
        "analytics": f"{base}/analytics/",
        "settings": f"{base}/settings/",
    }


def _category_urls(organization, category):
    base = f"/o/{organization.slug}/categories/{category.id}"
    return {
        "detail": f"{base}/",
        "edit": f"{base}/edit/",
        "archive": f"{base}/archive/",
        "restore": f"{base}/restore/",
    }


def _offering_urls(organization, offering):
    base = f"/o/{organization.slug}/products/{offering.id}"
    return {
        "detail": f"{base}/",
        "edit": f"{base}/edit/",
        "archive": f"{base}/archive/",
        "restore": f"{base}/restore/",
    }


def _admin_payload(request, organization, navigation, **extra):
    payload = {
        "organization": organization,
        "navigation": navigation,
        "facility_profile": request.facility_profile,
        "admin_urls": _admin_urls(organization),
    }
    payload.update(extra)
    return payload


def _admin_category_context(request, organization_slug: str, category_id):
    organization, navigation = _organization_context(request, organization_slug)
    category = get_object_or_404(admin_category_for_organization(organization, category_id))
    return organization, navigation, category


def _admin_offering_context(request, organization_slug: str, offering_id):
    organization, navigation = _organization_context(request, organization_slug)
    offering = get_object_or_404(
        admin_offering_for_organization(organization, offering_id)
    )
    return organization, navigation, offering


def _admin_page_title(request, url_name: str, default: str) -> str:
    return page_title_for_url_name(
        profile=request.facility_profile,
        url_name=url_name,
        default=default,
    )


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


def _offering_audit_payload(offering):
    return {
        "name": offering.name,
        "code": offering.code,
        "status": offering.status,
        "offering_type": offering.offering_type,
        "base_price": str(offering.base_price),
        "currency": offering.currency,
        "visible_on_website": offering.visible_on_website,
        "whatsapp_inquiry_enabled": offering.whatsapp_inquiry_enabled,
        "facility_id": str(offering.facility_id) if offering.facility_id else "",
    }


def _category_audit_payload(category):
    return {
        "name": category.name,
        "slug": category.slug,
        "status": category.status,
        "parent_id": str(category.parent_id) if category.parent_id else "",
        "sort_order": category.sort_order,
        "facility_id": str(category.facility_id) if category.facility_id else "",
    }


def admin_dashboard(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    products = visible_offerings_for_organization(organization)[:5]
    recent_orders = Order.objects.for_organization(organization).order_by("-created_at")[:5]
    return render(
        request,
        "admin_portal/dashboard.html",
        _admin_payload(
            request,
            organization,
            navigation,
            products=products,
            recent_orders=recent_orders,
        ),
    )


def admin_marketplace(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    modules = visible_marketplace_modules(country=organization.country)
    return render(
        request,
        "admin_portal/marketplace.html",
        _admin_payload(request, organization, navigation, modules=modules),
    )


def admin_billing(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        _admin_payload(request, organization, navigation, title="Billing"),
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
        _admin_payload(request, organization, navigation, pages=pages),
    )


def admin_products(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    products = admin_offerings_for_organization(organization)
    return render(
        request,
        "admin_portal/products.html",
        _admin_payload(
            request,
            organization,
            navigation,
            products=products,
            title=_admin_page_title(request, "admin-products", "Products"),
        ),
    )


def admin_product_create(request, organization_slug: str):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation = _organization_context(request, organization_slug)
    form = OfferingAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            offering = create_offering(
                organization=organization,
                facility=request.facility,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.offering.created",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_offering", str(offering.id)),
                after={
                    "name": offering.name,
                    "code": offering.code,
                    "status": offering.status,
                    "offering_type": offering.offering_type,
                    "visible_on_website": offering.visible_on_website,
                    "facility_id": str(offering.facility_id) if offering.facility_id else "",
                    "facility_type": request.facility_profile.facility_type,
                },
                source="business_admin",
            )
            messages.success(
                request,
                f"{request.facility_profile.terms['offering']} created.",
            )
            return redirect(_admin_urls(organization)["products"])

    return render(
        request,
        "admin_portal/product_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
        ),
    )


def admin_product_detail(request, organization_slug: str, offering_id):
    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    default_variant = offering.variants.filter(is_default=True).order_by("created_at").first()
    return render(
        request,
        "admin_portal/product_detail.html",
        _admin_payload(
            request,
            organization,
            navigation,
            offering=offering,
            offering_urls=_offering_urls(organization, offering),
            default_variant=default_variant,
            title=offering.name,
            is_archived=offering.status == RecordStatus.ARCHIVED,
        ),
    )


def admin_product_edit(request, organization_slug: str, offering_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    form = OfferingAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        instance=offering,
    )
    if request.method == "POST" and form.is_valid():
        before = _offering_audit_payload(offering)
        try:
            offering = update_offering(
                organization=organization,
                offering=offering,
                facility=request.facility,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.offering.updated",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_offering", str(offering.id)),
                before=before,
                after=_offering_audit_payload(offering),
                source="business_admin",
            )
            messages.success(
                request,
                f"{request.facility_profile.terms['offering']} updated.",
            )
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/product_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
            offering=offering,
            cancel_url=_offering_urls(organization, offering)["detail"],
            return_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_product_archive(request, organization_slug: str, offering_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    before = _offering_audit_payload(offering)
    offering = archive_offering(
        organization=organization,
        offering=offering,
        archived_by=request.user,
    )
    audit_event(
        action="catalogue.offering.archived",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_offering", str(offering.id)),
        before=before,
        after=_offering_audit_payload(offering),
        source="business_admin",
    )
    messages.success(request, f"{request.facility_profile.terms['offering']} archived.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_product_restore(request, organization_slug: str, offering_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    before = _offering_audit_payload(offering)
    offering = restore_offering(
        organization=organization,
        offering=offering,
        restored_by=request.user,
    )
    audit_event(
        action="catalogue.offering.restored",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_offering", str(offering.id)),
        before=before,
        after=_offering_audit_payload(offering),
        source="business_admin",
    )
    messages.success(
        request,
        f"{request.facility_profile.terms['offering']} restored as draft.",
    )
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_categories(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    categories = admin_categories_for_organization(organization)
    return render(
        request,
        "admin_portal/categories.html",
        _admin_payload(
            request,
            organization,
            navigation,
            categories=categories,
            title=_admin_page_title(request, "admin-categories", "Categories"),
        ),
    )


def admin_category_create(request, organization_slug: str):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation = _organization_context(request, organization_slug)
    form = CategoryAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            category = create_category(
                organization=organization,
                facility=request.facility,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.category.created",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_category", str(category.id)),
                after=_category_audit_payload(category),
                source="business_admin",
            )
            messages.success(
                request,
                f"{request.facility_profile.terms['category']} created.",
            )
            return redirect(_category_urls(organization, category)["detail"])

    return render(
        request,
        "admin_portal/category_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
        ),
    )


def admin_category_detail(request, organization_slug: str, category_id):
    organization, navigation, category = _admin_category_context(
        request,
        organization_slug,
        category_id,
    )
    return render(
        request,
        "admin_portal/category_detail.html",
        _admin_payload(
            request,
            organization,
            navigation,
            category=category,
            category_urls=_category_urls(organization, category),
            offering_count=category.offerings.count(),
            child_count=category.children.exclude(status=RecordStatus.DELETED).count(),
            title=category.name,
            is_archived=category.status == RecordStatus.ARCHIVED,
        ),
    )


def admin_category_edit(request, organization_slug: str, category_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, category = _admin_category_context(
        request,
        organization_slug,
        category_id,
    )
    form = CategoryAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        instance=category,
    )
    if request.method == "POST" and form.is_valid():
        before = _category_audit_payload(category)
        try:
            category = update_category(
                organization=organization,
                category=category,
                facility=request.facility,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.category.updated",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_category", str(category.id)),
                before=before,
                after=_category_audit_payload(category),
                source="business_admin",
            )
            messages.success(
                request,
                f"{request.facility_profile.terms['category']} updated.",
            )
            return redirect(_category_urls(organization, category)["detail"])

    return render(
        request,
        "admin_portal/category_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
            category=category,
            cancel_url=_category_urls(organization, category)["detail"],
            return_url=_category_urls(organization, category)["detail"],
        ),
    )


def admin_category_archive(request, organization_slug: str, category_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, category = _admin_category_context(
        request,
        organization_slug,
        category_id,
    )
    before = _category_audit_payload(category)
    category = archive_category(
        organization=organization,
        category=category,
        archived_by=request.user,
    )
    audit_event(
        action="catalogue.category.archived",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_category", str(category.id)),
        before=before,
        after=_category_audit_payload(category),
        source="business_admin",
    )
    messages.success(request, f"{request.facility_profile.terms['category']} archived.")
    return redirect(_category_urls(organization, category)["detail"])


def admin_category_restore(request, organization_slug: str, category_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, category = _admin_category_context(
        request,
        organization_slug,
        category_id,
    )
    before = _category_audit_payload(category)
    category = restore_category(
        organization=organization,
        category=category,
        restored_by=request.user,
    )
    audit_event(
        action="catalogue.category.restored",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_category", str(category.id)),
        before=before,
        after=_category_audit_payload(category),
        source="business_admin",
    )
    messages.success(
        request,
        f"{request.facility_profile.terms['category']} restored as draft.",
    )
    return redirect(_category_urls(organization, category)["detail"])


def admin_inventory(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        _admin_payload(
            request,
            organization,
            navigation,
            title=_admin_page_title(request, "admin-inventory", "Inventory"),
        ),
    )


def admin_orders(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    orders = Order.objects.for_organization(organization).order_by("-created_at")
    return render(
        request,
        "admin_portal/orders.html",
        _admin_payload(
            request,
            organization,
            navigation,
            orders=orders,
            title=_admin_page_title(request, "admin-orders", "Orders"),
        ),
    )


def admin_payments(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        _admin_payload(request, organization, navigation, title="Payments"),
    )


def admin_analytics(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        _admin_payload(request, organization, navigation, title="Analytics"),
    )


def admin_settings(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    return render(
        request,
        "admin_portal/simple_page.html",
        _admin_payload(request, organization, navigation, title="Settings"),
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
