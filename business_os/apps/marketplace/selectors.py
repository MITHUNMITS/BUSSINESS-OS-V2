from business_os.apps.marketplace.models import Module


def visible_marketplace_modules(country: str | None = None):
    queryset = Module.objects.filter(visible_in_marketplace=True, release_status="public")
    if country:
        queryset = queryset.filter(supported_countries__contains=[country])
    return queryset.prefetch_related("module_capabilities__capability", "prices")

