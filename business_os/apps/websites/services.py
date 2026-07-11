from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from business_os.apps.entitlements.services import has_entitlement
from business_os.apps.websites.domain_services import generated_domain_for_slug
from business_os.apps.websites.models import (
    Website,
    WebsiteDomain,
    WebsitePage,
    WebsiteSection,
    WebsiteTheme,
    WebsiteVersion,
)

DEFAULT_THEME_TOKENS = {
    "primary": "#1f7a68",
    "secondary": "#2f4f64",
    "accent": "#b7791f",
    "background": "#ffffff",
    "surface": "#f7f7f5",
    "text": "#111827",
    "muted_text": "#6b7280",
    "heading_font": "Inter",
    "body_font": "Inter",
    "card_radius": "8px",
    "button_radius": "6px",
}


@transaction.atomic
def provision_default_website(*, organization: Any, owner: Any | None = None) -> Website:
    website, created = Website.objects.get_or_create(
        organization=organization,
        defaults={
            "slug": organization.slug,
            "name": organization.name,
            "status": "active",
            "default_locale": organization.default_locale,
        },
    )
    if created:
        WebsiteTheme.objects.create(
            organization=organization,
            website=website,
            tokens=DEFAULT_THEME_TOKENS,
            created_by=owner,
        )
        homepage = WebsitePage.objects.create(
            organization=organization,
            website=website,
            slug="home",
            title="Home",
            is_homepage=True,
            status="active",
            created_by=owner,
        )
        WebsiteSection.objects.create(
            organization=organization,
            page=homepage,
            section_type="hero",
            variant="fashion_editorial",
            content={"heading": organization.name, "cta_label": "Shop collection"},
            created_by=owner,
        )
        WebsitePage.objects.create(
            organization=organization,
            website=website,
            slug="shop",
            title="Shop",
            required_capability="catalogue.basic",
            status="active",
            created_by=owner,
            sort_order=10,
        )
        WebsitePage.objects.create(
            organization=organization,
            website=website,
            slug="cart",
            title="Cart",
            required_capability="commerce.cart",
            status="active",
            created_by=owner,
            sort_order=20,
        )
        WebsitePage.objects.create(
            organization=organization,
            website=website,
            slug="contact",
            title="Contact",
            status="active",
            created_by=owner,
            sort_order=90,
        )
    WebsiteDomain.objects.get_or_create(
        organization=organization,
        website=website,
        domain_name=generated_domain_for_slug(website.slug),
        defaults={
            "domain_type": WebsiteDomain.DomainType.GENERATED,
            "domain_status": WebsiteDomain.DomainStatus.ACTIVE,
            "is_primary": not bool(website.primary_domain),
            "created_by": owner,
        },
    )
    return website


def visible_pages_for_website(*, website: Website):
    pages = website.pages.filter(status="active").order_by("sort_order")
    visible_ids = []
    for page in pages:
        if not page.required_capability or has_entitlement(
            organization=website.organization,
            capability_code=page.required_capability,
        ):
            visible_ids.append(page.id)
    return pages.filter(id__in=visible_ids)


@transaction.atomic
def publish_website(*, website: Website, user: Any | None = None) -> WebsiteVersion:
    snapshot = {
        "website": {"slug": website.slug, "template_pack": website.template_pack},
        "pages": [
            {
                "slug": page.slug,
                "title": page.title,
                "sections": [
                    {
                        "type": section.section_type,
                        "variant": section.variant,
                        "content": section.content,
                    }
                    for section in page.sections.all()
                ],
            }
            for page in website.pages.prefetch_related("sections").all()
        ],
    }
    version_number = website.published_version + 1
    version = WebsiteVersion.objects.create(
        organization=website.organization,
        website=website,
        version_number=version_number,
        snapshot=snapshot,
        published_by=user,
        published_at=timezone.now(),
    )
    website.published_version = version_number
    website.status = "active"
    website.save(update_fields=["published_version", "status", "updated_at"])
    return version


def page_slug_for_title(title: str) -> str:
    return slugify(title)[:120]
