from business_os.apps.catalogue.models import Offering
from business_os.apps.core.models import RecordStatus


def admin_offerings_for_organization(organization):
    return (
        Offering.objects.for_organization(organization)
        .exclude(status=RecordStatus.DELETED)
        .select_related("category", "facility")
        .prefetch_related("variants", "images")
        .order_by("-updated_at", "name")
    )


def visible_offerings_for_organization(organization):
    return (
        Offering.objects.for_organization(organization)
        .filter(status="active", visible_on_website=True)
        .select_related("category")
        .prefetch_related("variants", "images")
        .order_by("name")
    )
