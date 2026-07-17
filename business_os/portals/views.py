from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from business_os.apps.catalogue.forms import (
    CategoryAdminForm,
    CollectionAdminForm,
    OfferingAdminForm,
    OfferingVariantAdminForm,
    OptionDefinitionAdminForm,
    OptionValueAdminForm,
)
from business_os.apps.catalogue.selectors import (
    admin_categories_for_organization,
    admin_category_for_organization,
    admin_collection_for_organization,
    admin_collections_for_organization,
    admin_offering_for_organization,
    admin_offerings_for_organization,
    admin_option_for_organization,
    admin_option_value_for_option,
    admin_options_for_organization,
    admin_variant_for_offering,
    admin_variants_for_offering,
    visible_offerings_for_organization,
)
from business_os.apps.catalogue.services import (
    archive_category,
    archive_collection,
    archive_offering,
    archive_offering_variant,
    archive_option_definition,
    archive_option_value,
    create_category,
    create_collection,
    create_offering,
    create_offering_variant,
    create_option_definition,
    create_option_value,
    restore_category,
    restore_collection,
    restore_offering,
    restore_offering_variant,
    restore_option_definition,
    restore_option_value,
    update_category,
    update_collection,
    update_offering,
    update_offering_variant,
    update_option_definition,
    update_option_value,
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
from business_os.apps.entitlements.services import has_entitlement
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
        "collections": f"{base}/collections/",
        "collections_create": f"{base}/collections/new/",
        "inventory": f"{base}/inventory/",
        "orders": f"{base}/orders/",
        "payments": f"{base}/payments/",
        "analytics": f"{base}/analytics/",
        "settings": f"{base}/settings/",
    }


def _collection_urls(organization, collection):
    base = f"/o/{organization.slug}/collections/{collection.id}"
    return {
        "detail": f"{base}/",
        "edit": f"{base}/edit/",
        "archive": f"{base}/archive/",
        "restore": f"{base}/restore/",
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
        "options_create": f"{base}/options/new/",
        "variants_create": f"{base}/variants/new/",
    }


def _option_urls(organization, offering, option):
    base = f"/o/{organization.slug}/products/{offering.id}/options/{option.id}"
    return {
        "edit": f"{base}/edit/",
        "archive": f"{base}/archive/",
        "restore": f"{base}/restore/",
        "values_create": f"{base}/values/new/",
    }


def _option_value_urls(organization, offering, option, option_value):
    base = (
        f"/o/{organization.slug}/products/{offering.id}/options/"
        f"{option.id}/values/{option_value.id}"
    )
    return {
        "edit": f"{base}/edit/",
        "archive": f"{base}/archive/",
        "restore": f"{base}/restore/",
    }


def _variant_urls(organization, offering, variant):
    base = f"/o/{organization.slug}/products/{offering.id}/variants/{variant.id}"
    return {
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


def _admin_collection_context(request, organization_slug: str, collection_id):
    organization, navigation = _organization_context(request, organization_slug)
    collection = get_object_or_404(
        admin_collection_for_organization(organization, collection_id)
    )
    return organization, navigation, collection


def _admin_offering_context(request, organization_slug: str, offering_id):
    organization, navigation = _organization_context(request, organization_slug)
    offering = get_object_or_404(
        admin_offering_for_organization(organization, offering_id)
    )
    return organization, navigation, offering


def _admin_option_context(request, organization_slug: str, offering_id, option_id):
    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    _require_variants_entitlement(request, organization)
    option = get_object_or_404(
        admin_option_for_organization(
            organization,
            option_id,
            facility=offering.facility,
        )
    )
    return organization, navigation, offering, option


def _admin_option_value_context(
    request,
    organization_slug: str,
    offering_id,
    option_id,
    value_id,
):
    organization, navigation, offering, option = _admin_option_context(
        request,
        organization_slug,
        offering_id,
        option_id,
    )
    option_value = get_object_or_404(admin_option_value_for_option(option, value_id))
    return organization, navigation, offering, option, option_value


def _admin_variant_context(request, organization_slug: str, offering_id, variant_id):
    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    _require_variants_entitlement(request, organization)
    variant = get_object_or_404(
        admin_variant_for_offering(organization, offering, variant_id)
    )
    return organization, navigation, offering, variant


def _admin_page_title(request, url_name: str, default: str) -> str:
    return page_title_for_url_name(
        profile=request.facility_profile,
        url_name=url_name,
        default=default,
    )


def _require_platform_portal_access(request) -> None:
    require_platform_permission(request.user, PlatformPermission.PORTAL_ACCESS)


def _has_variants_entitlement(request, organization) -> bool:
    return has_entitlement(
        organization=organization,
        facility=getattr(request, "facility", None),
        capability_code="catalogue.variants",
    )


def _require_variants_entitlement(request, organization) -> None:
    if not _has_variants_entitlement(request, organization):
        raise PermissionDenied("Catalogue variants entitlement is required.")


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


def _option_audit_payload(option):
    return {
        "name": option.name,
        "code": option.code,
        "status": option.status,
        "sort_order": option.sort_order,
        "facility_id": str(option.facility_id) if option.facility_id else "",
    }


def _option_value_audit_payload(option_value):
    return {
        "option_id": str(option_value.option_id),
        "label": option_value.label,
        "value": option_value.value,
        "color_hex": option_value.color_hex,
        "status": option_value.status,
        "sort_order": option_value.sort_order,
        "facility_id": str(option_value.facility_id) if option_value.facility_id else "",
    }


def _variant_audit_payload(variant):
    option_value_ids = [
        str(value_id)
        for value_id in (
            variant.option_values.order_by("option__sort_order", "sort_order").values_list(
                "id",
                flat=True,
            )
        )
    ]
    return {
        "offering_id": str(variant.offering_id),
        "sku": variant.sku,
        "title": variant.title,
        "status": variant.status,
        "is_default": variant.is_default,
        "price_override": str(variant.price_override) if variant.price_override is not None else "",
        "stock_tracking_enabled": variant.stock_tracking_enabled,
        "option_value_ids": option_value_ids,
        "facility_id": str(variant.facility_id) if variant.facility_id else "",
    }


def _collection_audit_payload(collection):
    offering_ids = [
        str(offering_id)
        for offering_id in collection.items.order_by("sort_order").values_list(
            "offering_id",
            flat=True,
        )
    ]
    return {
        "name": collection.name,
        "slug": collection.slug,
        "status": collection.status,
        "offering_ids": offering_ids,
        "offering_count": len(offering_ids),
        "facility_id": str(collection.facility_id) if collection.facility_id else "",
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
    has_variants_entitlement = _has_variants_entitlement(request, organization)
    options = []
    variants = []
    if has_variants_entitlement:
        options = admin_options_for_organization(
            organization,
            facility=offering.facility,
        )
        variants = admin_variants_for_offering(offering)
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
            options=options,
            variants=variants,
            has_variants_entitlement=has_variants_entitlement,
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


def admin_option_create(request, organization_slug: str, offering_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    _require_variants_entitlement(request, organization)
    form = OptionDefinitionAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            option = create_option_definition(
                organization=organization,
                facility=offering.facility,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.option.created",
                request=request,
                organization=organization,
                facility=offering.facility,
                actor=request.user,
                target=AuditTarget("catalogue_option", str(option.id)),
                after=_option_audit_payload(option),
                source="business_admin",
            )
            messages.success(request, "Option created.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/option_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_option_edit(request, organization_slug: str, offering_id, option_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering, option = _admin_option_context(
        request,
        organization_slug,
        offering_id,
        option_id,
    )
    form = OptionDefinitionAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        instance=option,
    )
    if request.method == "POST" and form.is_valid():
        before = _option_audit_payload(option)
        try:
            option = update_option_definition(
                organization=organization,
                option_definition=option,
                facility=offering.facility,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.option.updated",
                request=request,
                organization=organization,
                facility=offering.facility,
                actor=request.user,
                target=AuditTarget("catalogue_option", str(option.id)),
                before=before,
                after=_option_audit_payload(option),
                source="business_admin",
            )
            messages.success(request, "Option updated.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/option_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            option=option,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_option_archive(request, organization_slug: str, offering_id, option_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, option = _admin_option_context(
        request,
        organization_slug,
        offering_id,
        option_id,
    )
    before = _option_audit_payload(option)
    option = archive_option_definition(
        organization=organization,
        option_definition=option,
        archived_by=request.user,
    )
    audit_event(
        action="catalogue.option.archived",
        request=request,
        organization=organization,
        facility=offering.facility,
        actor=request.user,
        target=AuditTarget("catalogue_option", str(option.id)),
        before=before,
        after=_option_audit_payload(option),
        source="business_admin",
    )
    messages.success(request, "Option archived.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_option_restore(request, organization_slug: str, offering_id, option_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, option = _admin_option_context(
        request,
        organization_slug,
        offering_id,
        option_id,
    )
    before = _option_audit_payload(option)
    option = restore_option_definition(
        organization=organization,
        option_definition=option,
        restored_by=request.user,
    )
    audit_event(
        action="catalogue.option.restored",
        request=request,
        organization=organization,
        facility=offering.facility,
        actor=request.user,
        target=AuditTarget("catalogue_option", str(option.id)),
        before=before,
        after=_option_audit_payload(option),
        source="business_admin",
    )
    messages.success(request, "Option restored as draft.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_option_value_create(request, organization_slug: str, offering_id, option_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering, option = _admin_option_context(
        request,
        organization_slug,
        offering_id,
        option_id,
    )
    form = OptionValueAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        option=option,
    )
    if request.method == "POST" and form.is_valid():
        try:
            option_value = create_option_value(
                organization=organization,
                option_definition=option,
                facility=option.facility,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.option_value.created",
                request=request,
                organization=organization,
                facility=option.facility,
                actor=request.user,
                target=AuditTarget("catalogue_option_value", str(option_value.id)),
                after=_option_value_audit_payload(option_value),
                source="business_admin",
            )
            messages.success(request, "Option value created.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/option_value_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            option=option,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_option_value_edit(request, organization_slug: str, offering_id, option_id, value_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering, option, option_value = _admin_option_value_context(
        request,
        organization_slug,
        offering_id,
        option_id,
        value_id,
    )
    form = OptionValueAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        option=option,
        instance=option_value,
    )
    if request.method == "POST" and form.is_valid():
        before = _option_value_audit_payload(option_value)
        try:
            option_value = update_option_value(
                organization=organization,
                option_value=option_value,
                facility=option.facility,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.option_value.updated",
                request=request,
                organization=organization,
                facility=option.facility,
                actor=request.user,
                target=AuditTarget("catalogue_option_value", str(option_value.id)),
                before=before,
                after=_option_value_audit_payload(option_value),
                source="business_admin",
            )
            messages.success(request, "Option value updated.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/option_value_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            option=option,
            option_value=option_value,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_option_value_archive(request, organization_slug: str, offering_id, option_id, value_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, option, option_value = _admin_option_value_context(
        request,
        organization_slug,
        offering_id,
        option_id,
        value_id,
    )
    before = _option_value_audit_payload(option_value)
    option_value = archive_option_value(
        organization=organization,
        option_value=option_value,
        archived_by=request.user,
    )
    audit_event(
        action="catalogue.option_value.archived",
        request=request,
        organization=organization,
        facility=option.facility,
        actor=request.user,
        target=AuditTarget("catalogue_option_value", str(option_value.id)),
        before=before,
        after=_option_value_audit_payload(option_value),
        source="business_admin",
    )
    messages.success(request, "Option value archived.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_option_value_restore(request, organization_slug: str, offering_id, option_id, value_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, option, option_value = _admin_option_value_context(
        request,
        organization_slug,
        offering_id,
        option_id,
        value_id,
    )
    before = _option_value_audit_payload(option_value)
    option_value = restore_option_value(
        organization=organization,
        option_value=option_value,
        restored_by=request.user,
    )
    audit_event(
        action="catalogue.option_value.restored",
        request=request,
        organization=organization,
        facility=option.facility,
        actor=request.user,
        target=AuditTarget("catalogue_option_value", str(option_value.id)),
        before=before,
        after=_option_value_audit_payload(option_value),
        source="business_admin",
    )
    messages.success(request, "Option value restored as draft.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_variant_create(request, organization_slug: str, offering_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering = _admin_offering_context(
        request,
        organization_slug,
        offering_id,
    )
    _require_variants_entitlement(request, organization)
    form = OfferingVariantAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        offering=offering,
    )
    if request.method == "POST" and form.is_valid():
        try:
            variant = create_offering_variant(
                organization=organization,
                offering=offering,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.variant.created",
                request=request,
                organization=organization,
                facility=offering.facility,
                actor=request.user,
                target=AuditTarget("catalogue_variant", str(variant.id)),
                after=_variant_audit_payload(variant),
                source="business_admin",
            )
            messages.success(request, "Variant created.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/variant_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_variant_edit(request, organization_slug: str, offering_id, variant_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, offering, variant = _admin_variant_context(
        request,
        organization_slug,
        offering_id,
        variant_id,
    )
    form = OfferingVariantAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        offering=offering,
        instance=variant,
    )
    if request.method == "POST" and form.is_valid():
        before = _variant_audit_payload(variant)
        try:
            variant = update_offering_variant(
                organization=organization,
                variant=variant,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.variant.updated",
                request=request,
                organization=organization,
                facility=offering.facility,
                actor=request.user,
                target=AuditTarget("catalogue_variant", str(variant.id)),
                before=before,
                after=_variant_audit_payload(variant),
                source="business_admin",
            )
            messages.success(request, "Variant updated.")
            return redirect(_offering_urls(organization, offering)["detail"])

    return render(
        request,
        "admin_portal/variant_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            offering=offering,
            variant=variant,
            title=form.schema.page_title,
            return_url=_offering_urls(organization, offering)["detail"],
            cancel_url=_offering_urls(organization, offering)["detail"],
        ),
    )


def admin_variant_archive(request, organization_slug: str, offering_id, variant_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, variant = _admin_variant_context(
        request,
        organization_slug,
        offering_id,
        variant_id,
    )
    before = _variant_audit_payload(variant)
    try:
        variant = archive_offering_variant(
            organization=organization,
            variant=variant,
            archived_by=request.user,
        )
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        audit_event(
            action="catalogue.variant.archived",
            request=request,
            organization=organization,
            facility=offering.facility,
            actor=request.user,
            target=AuditTarget("catalogue_variant", str(variant.id)),
            before=before,
            after=_variant_audit_payload(variant),
            source="business_admin",
        )
        messages.success(request, "Variant archived.")
    return redirect(_offering_urls(organization, offering)["detail"])


def admin_variant_restore(request, organization_slug: str, offering_id, variant_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, offering, variant = _admin_variant_context(
        request,
        organization_slug,
        offering_id,
        variant_id,
    )
    before = _variant_audit_payload(variant)
    try:
        variant = restore_offering_variant(
            organization=organization,
            variant=variant,
            restored_by=request.user,
        )
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        audit_event(
            action="catalogue.variant.restored",
            request=request,
            organization=organization,
            facility=offering.facility,
            actor=request.user,
            target=AuditTarget("catalogue_variant", str(variant.id)),
            before=before,
            after=_variant_audit_payload(variant),
            source="business_admin",
        )
        messages.success(request, "Variant restored as draft.")
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


def admin_collections(request, organization_slug: str):
    organization, navigation = _organization_context(request, organization_slug)
    collections = admin_collections_for_organization(organization)
    return render(
        request,
        "admin_portal/collections.html",
        _admin_payload(
            request,
            organization,
            navigation,
            collections=collections,
            title=_admin_page_title(request, "admin-collections", "Collections"),
        ),
    )


def admin_collection_create(request, organization_slug: str):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation = _organization_context(request, organization_slug)
    form = CollectionAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            collection = create_collection(
                organization=organization,
                facility=request.facility,
                created_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.collection.created",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_collection", str(collection.id)),
                after=_collection_audit_payload(collection),
                source="business_admin",
            )
            messages.success(request, "Collection created.")
            return redirect(_collection_urls(organization, collection)["detail"])

    return render(
        request,
        "admin_portal/collection_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
        ),
    )


def admin_collection_detail(request, organization_slug: str, collection_id):
    organization, navigation, collection = _admin_collection_context(
        request,
        organization_slug,
        collection_id,
    )
    collection_items = collection.items.order_by("sort_order").select_related("offering")
    return render(
        request,
        "admin_portal/collection_detail.html",
        _admin_payload(
            request,
            organization,
            navigation,
            collection=collection,
            collection_urls=_collection_urls(organization, collection),
            collection_items=collection_items,
            title=collection.name,
            is_archived=collection.status == RecordStatus.ARCHIVED,
        ),
    )


def admin_collection_edit(request, organization_slug: str, collection_id):
    if request.method not in {"GET", "POST"}:
        return HttpResponseNotAllowed(["GET", "POST"])

    organization, navigation, collection = _admin_collection_context(
        request,
        organization_slug,
        collection_id,
    )
    form = CollectionAdminForm(
        request.POST if request.method == "POST" else None,
        organization=organization,
        facility_profile=request.facility_profile,
        instance=collection,
    )
    if request.method == "POST" and form.is_valid():
        before = _collection_audit_payload(collection)
        try:
            collection = update_collection(
                organization=organization,
                collection=collection,
                facility=request.facility,
                updated_by=request.user,
                **form.to_service_kwargs(),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            audit_event(
                action="catalogue.collection.updated",
                request=request,
                organization=organization,
                facility=request.facility,
                actor=request.user,
                target=AuditTarget("catalogue_collection", str(collection.id)),
                before=before,
                after=_collection_audit_payload(collection),
                source="business_admin",
            )
            messages.success(request, "Collection updated.")
            return redirect(_collection_urls(organization, collection)["detail"])

    return render(
        request,
        "admin_portal/collection_form.html",
        _admin_payload(
            request,
            organization,
            navigation,
            form=form,
            form_schema=form.schema,
            title=form.schema.page_title,
            collection=collection,
            cancel_url=_collection_urls(organization, collection)["detail"],
            return_url=_collection_urls(organization, collection)["detail"],
        ),
    )


def admin_collection_archive(request, organization_slug: str, collection_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, collection = _admin_collection_context(
        request,
        organization_slug,
        collection_id,
    )
    before = _collection_audit_payload(collection)
    collection = archive_collection(
        organization=organization,
        collection=collection,
        archived_by=request.user,
    )
    audit_event(
        action="catalogue.collection.archived",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_collection", str(collection.id)),
        before=before,
        after=_collection_audit_payload(collection),
        source="business_admin",
    )
    messages.success(request, "Collection archived.")
    return redirect(_collection_urls(organization, collection)["detail"])


def admin_collection_restore(request, organization_slug: str, collection_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    organization, _navigation, collection = _admin_collection_context(
        request,
        organization_slug,
        collection_id,
    )
    before = _collection_audit_payload(collection)
    collection = restore_collection(
        organization=organization,
        collection=collection,
        restored_by=request.user,
    )
    audit_event(
        action="catalogue.collection.restored",
        request=request,
        organization=organization,
        facility=request.facility,
        actor=request.user,
        target=AuditTarget("catalogue_collection", str(collection.id)),
        before=before,
        after=_collection_audit_payload(collection),
        source="business_admin",
    )
    messages.success(request, "Collection restored as draft.")
    return redirect(_collection_urls(organization, collection)["detail"])


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
