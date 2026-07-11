import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

from business_os.apps.organizations.models import Membership, Organization
from business_os.apps.websites.domain_services import (
    generated_domain_for_slug,
    resolve_host,
)
from business_os.apps.websites.models import WebsiteDomain
from business_os.apps.websites.services import provision_default_website


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_generated_subdomain_resolves_to_website():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    website = provision_default_website(organization=organization)

    resolution = resolve_host(generated_domain_for_slug(website.slug))

    assert resolution.surface == "generated_site"
    assert resolution.website == website


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_custom_domain_resolves_only_when_active():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    website = provision_default_website(organization=organization)
    WebsiteDomain.objects.create(
        organization=organization,
        website=website,
        domain_name="www.novafashion.test",
        domain_type=WebsiteDomain.DomainType.CUSTOM,
        domain_status=WebsiteDomain.DomainStatus.ACTIVE,
        is_primary=True,
    )

    resolution = resolve_host("www.novafashion.test")

    assert resolution.surface == "custom_site"
    assert resolution.website == website


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_public_generated_host_does_not_expose_admin_routes():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="nova.businessos.local")

    response = client.get("/o/nova/dashboard/")

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_generated_host_root_renders_public_website():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="nova.businessos.local")

    response = client.get("/")

    assert response.status_code == 200
    assert b"Nova" in response.content


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_generated_host_uses_canonical_public_page_paths():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="nova.businessos.local")

    response = client.get("/p/contact/")

    assert response.status_code == 200
    assert b"Contact" in response.content


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_generated_host_rejects_local_slug_public_paths():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    provision_default_website(organization=organization)
    client = Client(HTTP_HOST="nova.businessos.local")

    response = client.get("/sites/nova/")

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_business_admin_host_allows_canonical_admin_route():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="not-used",
    )
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    Membership.objects.create(
        organization=organization,
        user=user,
        is_owner=True,
    )
    client = Client(HTTP_HOST="app.businessos.local")
    client.force_login(user)

    response = client.get("/o/nova/dashboard/")

    assert response.status_code == 200
    assert response.headers["X-BusinessOS-Surface"] == "business_admin"


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_business_admin_host_rejects_legacy_prefixed_admin_route():
    client = Client(HTTP_HOST="app.businessos.local")

    response = client.get("/app/o/nova/dashboard/")

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_api_host_rejects_business_admin_routes():
    client = Client(HTTP_HOST="api.businessos.local")

    response = client.get("/o/nova/dashboard/")

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_api_host_allows_versioned_api_routes():
    client = Client(HTTP_HOST="api.businessos.local")

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["X-BusinessOS-Surface"] == "api"


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_platform_host_requires_platform_staff():
    client = Client(HTTP_HOST="platform.businessos.local")

    response = client.get("/organizations/")

    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(PLATFORM_ROOT_DOMAIN="businessos.local", ALLOWED_HOSTS=[".businessos.local"])
def test_platform_host_allows_platform_staff_on_canonical_routes():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="platform-admin",
        email="platform@example.com",
        password="not-used",
        is_platform_staff=True,
    )
    client = Client(HTTP_HOST="platform.businessos.local")
    client.force_login(user)

    response = client.get("/organizations/")

    assert response.status_code == 200
    assert response.headers["X-BusinessOS-Surface"] == "platform_admin"
