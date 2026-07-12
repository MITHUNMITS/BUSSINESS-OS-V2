from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from business_os.apps.websites.models import Website, WebsiteDomain

LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "web"}
RESERVED_SUBDOMAINS = {
    "app": "business_admin",
    "platform": "platform_admin",
    "api": "api",
    "docs": "docs",
    "status": "status",
}
COMMON_EXACT_PATHS = {"/", "/favicon.ico", "/robots.txt"}
COMMON_PREFIXES = ("/health/", "/static/", "/media/")
SURFACE_ALLOWED_PREFIXES = {
    "marketing": (),
    "business_admin": ("/o/", "/login/", "/logout/", "/password-reset/"),
    "platform_admin": (
        "/modules/",
        "/organizations/",
        "/django-admin/",
        "/login/",
        "/logout/",
        "/password-reset/",
    ),
    "api": ("/api/v1/",),
    "docs": (),
    "status": (),
    "generated_site": (
        "/p/",
        "/account/",
        "/cart/",
        "/checkout/",
        "/orders/",
        "/products/",
        "/collections/",
        "/categories/",
        "/search/",
    ),
    "custom_site": (
        "/p/",
        "/account/",
        "/cart/",
        "/checkout/",
        "/orders/",
        "/products/",
        "/collections/",
        "/categories/",
        "/search/",
    ),
    "preview": ("/p/",),
    "unknown_generated_site": (),
    "unknown": (),
}


@dataclass(frozen=True)
class HostResolution:
    host: str
    surface: str
    website: Website | None = None
    site_slug: str = ""

    @property
    def is_public_site(self) -> bool:
        return self.surface in {"generated_site", "custom_site", "preview"}


def normalize_host(host: str) -> str:
    normalized = host.split(":", 1)[0].strip().lower().rstrip(".")
    return normalized


def platform_root_domain() -> str:
    return settings.PLATFORM_ROOT_DOMAIN.strip().lower().rstrip(".")


def generated_domain_for_slug(slug: str) -> str:
    return f"{slug}.{platform_root_domain()}"


def resolve_host(host: str) -> HostResolution:
    normalized = normalize_host(host)
    root_domain = platform_root_domain()

    if not normalized:
        return HostResolution(host=normalized, surface="unknown")
    if normalized in LOCAL_HOSTS:
        return HostResolution(host=normalized, surface="local")
    if normalized == root_domain:
        return HostResolution(host=normalized, surface="marketing")
    if normalized.endswith(".localhost"):
        return resolve_subdomain_host(
            host=normalized,
            subdomain=normalized.removesuffix(".localhost"),
        )

    reserved_suffix = f".{root_domain}"
    if normalized.endswith(reserved_suffix):
        return resolve_subdomain_host(
            host=normalized,
            subdomain=normalized[: -len(reserved_suffix)],
        )

    domain = (
        WebsiteDomain.objects.select_related("website", "website__organization")
        .filter(
            domain_name=normalized,
            domain_type=WebsiteDomain.DomainType.CUSTOM,
            domain_status=WebsiteDomain.DomainStatus.ACTIVE,
        )
        .first()
    )
    if domain:
        return HostResolution(
            host=normalized,
            surface="custom_site",
            website=domain.website,
            site_slug=domain.website.slug,
        )

    return HostResolution(host=normalized, surface="unknown")


def resolve_subdomain_host(*, host: str, subdomain: str) -> HostResolution:
    if subdomain in RESERVED_SUBDOMAINS:
        return HostResolution(host=host, surface=RESERVED_SUBDOMAINS[subdomain])
    if subdomain.endswith(".preview"):
        return HostResolution(host=host, surface="preview", site_slug=subdomain)

    website = Website.objects.filter(slug=subdomain).first()
    return HostResolution(
        host=host,
        surface="generated_site" if website else "unknown_generated_site",
        website=website,
        site_slug=subdomain,
    )


def public_host_for_website(website: Website) -> str:
    primary = website.domains.filter(
        is_primary=True,
        domain_status=WebsiteDomain.DomainStatus.ACTIVE,
    ).first()
    return primary.domain_name if primary else generated_domain_for_slug(website.slug)


def is_path_allowed_for_surface(*, surface: str, path: str) -> bool:
    if surface == "local":
        return True
    if path in COMMON_EXACT_PATHS or path.startswith(COMMON_PREFIXES):
        return True
    return path.startswith(SURFACE_ALLOWED_PREFIXES.get(surface, ()))
