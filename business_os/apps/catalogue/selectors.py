from business_os.apps.catalogue.models import Offering


def visible_offerings_for_organization(organization):
    return (
        Offering.objects.for_organization(organization)
        .filter(status="active", visible_on_website=True)
        .select_related("category")
        .prefetch_related("variants", "images")
        .order_by("name")
    )
