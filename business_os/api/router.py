from ninja import NinjaAPI, Schema
from ninja.errors import HttpError

from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.entitlements.services import has_entitlement
from business_os.apps.organizations.models import Organization

api = NinjaAPI(title="Business OS API", version="1.0.0")


class HealthSchema(Schema):
    status: str


class EntitlementSchema(Schema):
    organization: str
    capability: str
    active: bool


class ProductSchema(Schema):
    code: str
    name: str
    price: str
    currency: str


@api.get("/health", response=HealthSchema)
def api_health(request):
    return {"status": "ok"}


@api.get("/organizations/{organization_slug}/entitlements/{capability}", response=EntitlementSchema)
def api_entitlement(request, organization_slug: str, capability: str):
    organization = Organization.objects.get(slug=organization_slug)
    return {
        "organization": organization.slug,
        "capability": capability,
        "active": has_entitlement(organization=organization, capability_code=capability),
    }


@api.get("/organizations/{organization_slug}/catalogue/products", response=list[ProductSchema])
def api_products(request, organization_slug: str):
    organization = Organization.objects.get(slug=organization_slug)
    if not has_entitlement(organization=organization, capability_code="catalogue.basic"):
        raise HttpError(403, "Catalogue entitlement is required.")
    return [
        {
            "code": product.code,
            "name": product.name,
            "price": str(product.display_price),
            "currency": product.currency,
        }
        for product in visible_offerings_for_organization(organization)
    ]
