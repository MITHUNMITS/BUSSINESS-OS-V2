from django.http import Http404
from django.shortcuts import get_object_or_404, render

from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.entitlements.services import has_entitlement
from business_os.apps.websites.models import Website, WebsitePage
from business_os.apps.websites.services import visible_pages_for_website


def public_home(request, site_slug: str):
    website = get_object_or_404(Website.objects.select_related("organization"), slug=site_slug)
    pages = visible_pages_for_website(website=website)
    homepage = pages.filter(is_homepage=True).first()
    products = (
        visible_offerings_for_organization(website.organization)[:8]
        if has_entitlement(organization=website.organization, capability_code="catalogue.basic")
        else []
    )
    return render(
        request,
        "websites/public_home.html",
        {"website": website, "pages": pages, "homepage": homepage, "products": products},
    )


def public_page(request, site_slug: str, page_slug: str):
    website = get_object_or_404(Website.objects.select_related("organization"), slug=site_slug)
    page = get_object_or_404(WebsitePage, website=website, slug=page_slug, status="active")
    if page.required_capability and not has_entitlement(
        organization=website.organization,
        capability_code=page.required_capability,
    ):
        raise Http404("Page is not available for this website.")
    return render(request, "websites/public_page.html", {"website": website, "page": page})
