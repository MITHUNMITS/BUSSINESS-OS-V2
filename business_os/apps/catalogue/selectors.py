from django.db.models import Q

from business_os.apps.catalogue.models import (
    Category,
    Collection,
    Offering,
    OfferingVariant,
    OptionDefinition,
    OptionValue,
)
from business_os.apps.core.models import RecordStatus


def admin_categories_for_organization(organization):
    return (
        Category.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .select_related("parent", "facility")
        .order_by("sort_order", "name")
    )


def admin_category_for_organization(organization, category_id):
    return (
        Category.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .filter(id=category_id)
        .select_related("parent", "facility", "created_by", "updated_by")
    )


def admin_collections_for_organization(organization):
    return (
        Collection.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .select_related("facility")
        .prefetch_related("items", "offerings")
        .order_by("name")
    )


def admin_collection_for_organization(organization, collection_id):
    return (
        Collection.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .filter(id=collection_id)
        .select_related("facility", "created_by", "updated_by")
        .prefetch_related("items__offering", "offerings")
    )


def admin_offerings_for_organization(organization):
    return (
        Offering.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .select_related("category", "facility")
        .prefetch_related("variants", "images")
        .order_by("-updated_at", "name")
    )


def admin_offering_for_organization(organization, offering_id):
    return (
        Offering.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .filter(id=offering_id)
        .select_related("category", "facility", "created_by", "updated_by")
        .prefetch_related("variants", "images")
    )


def admin_options_for_organization(organization, *, facility=None):
    queryset = (
        OptionDefinition.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .select_related("facility")
        .prefetch_related("values")
        .order_by("sort_order", "name")
    )
    return _filter_facility_scope(queryset, facility=facility)


def admin_option_for_organization(organization, option_id, *, facility=None):
    queryset = (
        OptionDefinition.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .filter(id=option_id)
        .select_related("facility", "created_by", "updated_by")
        .prefetch_related("values")
    )
    return _filter_facility_scope(queryset, facility=facility)


def admin_option_value_for_option(option_definition, value_id):
    return (
        OptionValue.objects.filter(
            organization=option_definition.organization,
            option=option_definition,
        )
        .exclude(status=RecordStatus.DELETED)
        .filter(id=value_id)
        .select_related("option", "facility", "created_by", "updated_by")
    )


def admin_variants_for_offering(offering):
    return (
        OfferingVariant.objects.filter(
            organization=offering.organization,
            offering=offering,
        )
        .exclude(status=RecordStatus.DELETED)
        .select_related("offering", "facility", "created_by", "updated_by")
        .prefetch_related("option_values__option")
        .order_by("-is_default", "sku")
    )


def admin_variant_for_offering(organization, offering, variant_id):
    return (
        OfferingVariant.objects.filter(
            organization=organization,
            offering=offering,
        )
        .exclude(status=RecordStatus.DELETED)
        .filter(id=variant_id)
        .select_related("offering", "facility", "created_by", "updated_by")
        .prefetch_related("option_values__option")
    )


def visible_offerings_for_organization(organization):
    return (
        Offering.objects.for_organization(organization)
        .filter(status="active", visible_on_website=True)
        .select_related("category")
        .prefetch_related("variants", "images")
        .order_by("name")
    )


def _filter_facility_scope(queryset, *, facility=None):
    if facility is None:
        return queryset.filter(facility__isnull=True)
    return queryset.filter(Q(facility__isnull=True) | Q(facility=facility))
