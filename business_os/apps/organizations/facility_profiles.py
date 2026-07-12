from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from django.core.exceptions import PermissionDenied

from business_os.apps.core.models import RecordStatus
from business_os.apps.organizations.models import Facility, Organization


@dataclass(frozen=True)
class FacilityTerminologyPack:
    facility_type: str
    title: str
    terms: MappingProxyType[str, str]
    navigation_labels: MappingProxyType[str, str]
    dashboard_labels: MappingProxyType[str, str]
    page_titles: MappingProxyType[str, str]


@dataclass(frozen=True)
class FacilityProfile:
    organization: Organization
    facility: Facility | None
    facility_type: str
    terminology: FacilityTerminologyPack

    @property
    def terms(self) -> MappingProxyType[str, str]:
        return self.terminology.terms

    @property
    def navigation_labels(self) -> MappingProxyType[str, str]:
        return self.terminology.navigation_labels

    @property
    def dashboard_labels(self) -> MappingProxyType[str, str]:
        return self.terminology.dashboard_labels

    @property
    def page_titles(self) -> MappingProxyType[str, str]:
        return self.terminology.page_titles


DEFAULT_FACILITY_TYPE = Facility.FacilityType.ONLINE

TERMINOLOGY_PACKS: dict[str, FacilityTerminologyPack] = {
    Facility.FacilityType.ONLINE: FacilityTerminologyPack(
        facility_type=Facility.FacilityType.ONLINE,
        title="Online store",
        terms=MappingProxyType(
            {
                "customer": "Customer",
                "customers": "Customers",
                "offering": "Product",
                "offerings": "Products",
                "category": "Category",
                "categories": "Categories",
                "order": "Order",
                "orders": "Orders",
                "inventory": "Inventory",
            }
        ),
        navigation_labels=MappingProxyType(
            {
                "admin-products": "Products",
                "admin-categories": "Categories",
                "admin-orders": "Orders",
                "admin-inventory": "Inventory",
            }
        ),
        dashboard_labels=MappingProxyType(
            {
                "active_offerings": "Active products",
                "recent_orders": "Recent orders",
                "offerings_title": "Products",
                "orders_title": "Orders",
                "offering_column": "Product",
                "no_offerings_title": "No products yet",
                "no_offerings_message": "Add products to publish the first ecommerce catalogue.",
                "add_offering_action": "Add product",
                "no_orders_title": "No orders yet",
                "no_orders_message": "Orders will appear here once checkout is live.",
            }
        ),
        page_titles=MappingProxyType(
            {
                "admin-products": "Products",
                "admin-categories": "Categories",
                "admin-orders": "Orders",
                "admin-inventory": "Inventory",
            }
        ),
    ),
    Facility.FacilityType.RETAIL: FacilityTerminologyPack(
        facility_type=Facility.FacilityType.RETAIL,
        title="Retail store",
        terms=MappingProxyType(
            {
                "customer": "Customer",
                "customers": "Customers",
                "offering": "Product",
                "offerings": "Products",
                "category": "Department",
                "categories": "Departments",
                "order": "Sale",
                "orders": "Sales",
                "inventory": "Stock",
            }
        ),
        navigation_labels=MappingProxyType(
            {
                "admin-products": "Products",
                "admin-categories": "Departments",
                "admin-orders": "Sales",
                "admin-inventory": "Stock",
            }
        ),
        dashboard_labels=MappingProxyType(
            {
                "active_offerings": "Active products",
                "recent_orders": "Recent sales",
                "offerings_title": "Products",
                "orders_title": "Sales",
                "offering_column": "Product",
                "no_offerings_title": "No products yet",
                "no_offerings_message": "Add products before opening retail sales.",
                "add_offering_action": "Add product",
                "no_orders_title": "No sales yet",
                "no_orders_message": "Sales will appear here once checkout or POS is live.",
            }
        ),
        page_titles=MappingProxyType(
            {
                "admin-products": "Products",
                "admin-categories": "Departments",
                "admin-orders": "Sales",
                "admin-inventory": "Stock",
            }
        ),
    ),
    Facility.FacilityType.WAREHOUSE: FacilityTerminologyPack(
        facility_type=Facility.FacilityType.WAREHOUSE,
        title="Warehouse",
        terms=MappingProxyType(
            {
                "customer": "Account",
                "customers": "Accounts",
                "offering": "Item",
                "offerings": "Items",
                "category": "Item group",
                "categories": "Item groups",
                "order": "Fulfilment order",
                "orders": "Fulfilment orders",
                "inventory": "Stock",
            }
        ),
        navigation_labels=MappingProxyType(
            {
                "admin-products": "Items",
                "admin-categories": "Item groups",
                "admin-orders": "Fulfilment orders",
                "admin-inventory": "Stock",
            }
        ),
        dashboard_labels=MappingProxyType(
            {
                "active_offerings": "Active items",
                "recent_orders": "Recent fulfilment orders",
                "offerings_title": "Items",
                "orders_title": "Fulfilment orders",
                "offering_column": "Item",
                "no_offerings_title": "No items yet",
                "no_offerings_message": "Add items before managing warehouse stock.",
                "add_offering_action": "Add item",
                "no_orders_title": "No fulfilment orders yet",
                "no_orders_message": "Fulfilment orders will appear here once operations begin.",
            }
        ),
        page_titles=MappingProxyType(
            {
                "admin-products": "Items",
                "admin-categories": "Item groups",
                "admin-orders": "Fulfilment orders",
                "admin-inventory": "Stock",
            }
        ),
    ),
    Facility.FacilityType.OFFICE: FacilityTerminologyPack(
        facility_type=Facility.FacilityType.OFFICE,
        title="Office",
        terms=MappingProxyType(
            {
                "customer": "Client",
                "customers": "Clients",
                "offering": "Service",
                "offerings": "Services",
                "category": "Service area",
                "categories": "Service areas",
                "order": "Work request",
                "orders": "Work requests",
                "inventory": "Resources",
            }
        ),
        navigation_labels=MappingProxyType(
            {
                "admin-products": "Services",
                "admin-categories": "Service areas",
                "admin-orders": "Work requests",
                "admin-inventory": "Resources",
            }
        ),
        dashboard_labels=MappingProxyType(
            {
                "active_offerings": "Active services",
                "recent_orders": "Recent work requests",
                "offerings_title": "Services",
                "orders_title": "Work requests",
                "offering_column": "Service",
                "no_offerings_title": "No services yet",
                "no_offerings_message": "Add services before publishing office workflows.",
                "add_offering_action": "Add service",
                "no_orders_title": "No work requests yet",
                "no_orders_message": "Work requests will appear here once operations begin.",
            }
        ),
        page_titles=MappingProxyType(
            {
                "admin-products": "Services",
                "admin-categories": "Service areas",
                "admin-orders": "Work requests",
                "admin-inventory": "Resources",
            }
        ),
    ),
}


def resolve_facility_profile(
    *,
    organization: Organization,
    facility: Facility | None = None,
) -> FacilityProfile:
    resolved_facility = facility or _default_facility_for_organization(organization)
    if resolved_facility is not None and resolved_facility.organization_id != organization.id:
        raise PermissionDenied("Facility does not belong to this organization.")

    facility_type = _valid_facility_type(
        getattr(resolved_facility, "facility_type", None)
        or organization.metadata.get("primary_facility_type")
    )
    terminology = TERMINOLOGY_PACKS.get(facility_type, TERMINOLOGY_PACKS[DEFAULT_FACILITY_TYPE])
    return FacilityProfile(
        organization=organization,
        facility=resolved_facility,
        facility_type=terminology.facility_type,
        terminology=terminology,
    )


def label_for_url_name(
    *,
    profile: FacilityProfile,
    url_name: str,
    default: str,
) -> str:
    return profile.navigation_labels.get(url_name, default)


def page_title_for_url_name(
    *,
    profile: FacilityProfile,
    url_name: str,
    default: str,
) -> str:
    return profile.page_titles.get(url_name, default)


def _default_facility_for_organization(organization: Organization) -> Facility | None:
    return (
        Facility.objects.filter(
            organization=organization,
            status=RecordStatus.ACTIVE,
        )
        .order_by("code", "name")
        .first()
    )


def _valid_facility_type(value: Any) -> str:
    valid_types = {choice.value for choice in Facility.FacilityType}
    if value in valid_types:
        return str(value)
    return str(DEFAULT_FACILITY_TYPE)
