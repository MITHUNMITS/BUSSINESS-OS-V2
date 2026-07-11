from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from business_os.apps.catalogue.services import create_product
from business_os.apps.entitlements.services import grant_entitlement
from business_os.apps.inventory.models import InventoryItem, InventoryLevel
from business_os.apps.marketplace.models import Capability, Module, ModuleCapability
from business_os.apps.organizations.models import Facility, Membership, Organization
from business_os.apps.organizations.services import onboard_organization
from business_os.apps.payments.models import PaymentProvider
from business_os.apps.websites.services import provision_default_website, publish_website


class Command(BaseCommand):
    help = "Seed Business OS with production-shaped ecommerce launch data."

    @transaction.atomic
    def handle(self, *args, **options):
        modules = {
            "website": Module.objects.update_or_create(
                code="website",
                defaults={
                    "name": "Website & Content",
                    "category": "presence",
                    "description": "Public website, pages, themes, and publishing.",
                    "release_status": "public",
                    "visible_in_marketplace": True,
                    "supported_countries": ["AE", "IN"],
                },
            )[0],
            "catalogue": Module.objects.update_or_create(
                code="catalogue",
                defaults={
                    "name": "Catalogue & Offerings",
                    "category": "sell",
                    "description": "Products, categories, collections, variants, and images.",
                    "release_status": "public",
                    "visible_in_marketplace": True,
                    "supported_countries": ["AE", "IN"],
                },
            )[0],
            "commerce": Module.objects.update_or_create(
                code="commerce",
                defaults={
                    "name": "Commerce",
                    "category": "sell",
                    "description": "Cart, checkout, orders, shipping, and payments.",
                    "release_status": "public",
                    "visible_in_marketplace": True,
                    "supported_countries": ["AE", "IN"],
                },
            )[0],
        }
        capability_codes = [
            "website.basic",
            "website.pro",
            "catalogue.basic",
            "catalogue.variants",
            "catalogue.whatsapp_inquiry",
            "commerce.cart",
            "commerce.checkout",
            "commerce.orders",
            "commerce.guest_checkout",
            "inventory.basic",
            "payments.cod",
            "analytics.basic",
        ]
        capabilities = {}
        for code in capability_codes:
            capabilities[code] = Capability.objects.update_or_create(
                code=code,
                defaults={"name": code.replace(".", " ").title()},
            )[0]
        for code, module_code in [
            ("website.basic", "website"),
            ("website.pro", "website"),
            ("catalogue.basic", "catalogue"),
            ("catalogue.variants", "catalogue"),
            ("catalogue.whatsapp_inquiry", "catalogue"),
            ("commerce.cart", "commerce"),
            ("commerce.checkout", "commerce"),
            ("commerce.orders", "commerce"),
            ("commerce.guest_checkout", "commerce"),
        ]:
            ModuleCapability.objects.get_or_create(
                module=modules[module_code],
                capability=capabilities[code],
            )

        existing_organization = Organization.objects.filter(slug="nova-boutique").first()
        if existing_organization:
            organization = existing_organization
            facility = Facility.objects.get(organization=organization, code="online")
            owner_membership = Membership.objects.filter(
                organization=organization, is_owner=True
            ).first()
        else:
            result = onboard_organization(
                owner_email="owner@example.com",
                owner_username="owner",
                organization_name="Nova Boutique",
                country="AE",
                currency="AED",
                timezone="Asia/Dubai",
            )
            organization = result.organization
            facility = result.facility
            owner_membership = result.owner_membership
        owner = owner_membership.user if owner_membership else None
        website = provision_default_website(organization=organization, owner=owner)
        for code in capability_codes:
            grant_entitlement(organization=organization, facility=None, code=code, source="seed")

        PaymentProvider.objects.get_or_create(
            organization=organization,
            facility=facility,
            provider_type=PaymentProvider.ProviderType.COD,
            defaults={"name": "Cash on delivery", "active": True},
        )
        for index, name in enumerate(
            ["Linen Wrap Dress", "Silk Occasion Set", "Everyday Cotton Kurti"], start=1
        ):
            product_code = f"NOVA-{index:03d}"
            existing_product = organization.catalogue_offering_set.filter(code=product_code).first()
            product = existing_product or create_product(
                organization=organization,
                name=name,
                code=product_code,
                base_price=Decimal("249.00") + Decimal(index * 50),
                currency="AED",
                created_by=owner,
            )
            variant = product.variants.first()
            item, _created = InventoryItem.objects.get_or_create(
                organization=organization,
                facility=facility,
                variant=variant,
                defaults={"sku": variant.sku, "safety_stock": 1},
            )
            InventoryLevel.objects.get_or_create(
                organization=organization,
                facility=facility,
                item=item,
                defaults={"on_hand": 25, "safety_stock": 1},
            )
        publish_website(website=website, user=owner)
        self.stdout.write(self.style.SUCCESS("Seeded Business OS ecommerce launch data."))
