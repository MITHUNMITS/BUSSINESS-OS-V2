from django.http import Http404
from django.shortcuts import get_object_or_404, render

from business_os.apps.catalogue.selectors import visible_offerings_for_organization
from business_os.apps.entitlements.services import has_entitlement
from business_os.apps.websites.models import Website, WebsitePage
from business_os.apps.websites.services import visible_pages_for_website


def render_public_home(request, website: Website):
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


def public_home(request, site_slug: str):
    if getattr(request, "website", None) is not None and request.website.slug != site_slug:
        raise Http404("This website is not available on the current host.")
    website = get_object_or_404(Website.objects.select_related("organization"), slug=site_slug)
    return render_public_home(request, website)


def public_current_site_page(request, page_slug: str):
    website = getattr(request, "website", None)
    if website is None:
        raise Http404("A public website host is required.")
    return render_public_page(request, website, page_slug)


def public_page(request, site_slug: str, page_slug: str):
    if getattr(request, "website", None) is not None and request.website.slug != site_slug:
        raise Http404("This page is not available on the current host.")
    website = get_object_or_404(Website.objects.select_related("organization"), slug=site_slug)
    return render_public_page(request, website, page_slug)


def render_public_page(request, website: Website, page_slug: str):
    page = get_object_or_404(WebsitePage, website=website, slug=page_slug, status="active")
    if page.required_capability and not has_entitlement(
        organization=website.organization,
        capability_code=page.required_capability,
    ):
        raise Http404("Page is not available for this website.")
    return render(request, "websites/public_page.html", {"website": website, "page": page})
