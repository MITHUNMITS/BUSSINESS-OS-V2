import pytest

from business_os.apps.entitlements.services import grant_entitlement
from business_os.apps.organizations.models import Organization
from business_os.apps.websites.services import provision_default_website, visible_pages_for_website


@pytest.mark.django_db
def test_website_pages_follow_entitlements():
    organization = Organization.objects.create(slug="nova", name="Nova", default_currency="AED")
    website = provision_default_website(organization=organization)

    visible_slugs = {page.slug for page in visible_pages_for_website(website=website)}
    assert "home" in visible_slugs
    assert "shop" not in visible_slugs
    assert "cart" not in visible_slugs

    grant_entitlement(organization=organization, code="catalogue.basic")
    grant_entitlement(organization=organization, code="commerce.cart")

    visible_slugs = {page.slug for page in visible_pages_for_website(website=website)}
    assert "shop" in visible_slugs
    assert "cart" in visible_slugs
