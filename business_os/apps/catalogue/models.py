from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import RecordStatus, TenantOwnedModel


class Category(TenantOwnedModel):
    parent = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="children"
    )
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"], name="unique_category_slug_per_org"
            )
        ]
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Collection(TenantOwnedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160)
    description = models.TextField(blank=True)
    hero_image = models.ForeignKey(
        "core.MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collection_heroes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"], name="unique_collection_slug_per_org"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Offering(TenantOwnedModel):
    class OfferingType(models.TextChoices):
        PRODUCT = "product", _("Product")
        SERVICE = "service", _("Service")
        DIGITAL = "digital", _("Digital")

    offering_type = models.CharField(
        max_length=40, choices=OfferingType.choices, default=OfferingType.PRODUCT
    )
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180)
    code = models.CharField(max_length=80)
    summary = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True, related_name="offerings"
    )
    collections = models.ManyToManyField(
        Collection, through="CollectionItem", related_name="offerings", blank=True
    )
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="AED")
    tax_category = models.CharField(max_length=80, blank=True)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    visible_on_website = models.BooleanField(default=True)
    whatsapp_inquiry_enabled = models.BooleanField(default=True)
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"], name="unique_offering_slug_per_org"
            ),
            models.UniqueConstraint(
                fields=["organization", "code"], name="unique_offering_code_per_org"
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status", "visible_on_website"]),
            models.Index(fields=["organization", "category"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display_price(self):
        return self.sale_price if self.sale_price is not None else self.base_price


class CollectionItem(TenantOwnedModel):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="items")
    offering = models.ForeignKey(
        Offering, on_delete=models.CASCADE, related_name="collection_items"
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "collection", "offering"],
                name="unique_offering_per_collection",
            )
        ]


class OptionDefinition(TenantOwnedModel):
    name = models.CharField(max_length=80)
    code = models.SlugField(max_length=80)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"], name="unique_option_code_per_org"
            )
        ]

    def __str__(self) -> str:
        return self.name


class OptionValue(TenantOwnedModel):
    option = models.ForeignKey(OptionDefinition, on_delete=models.CASCADE, related_name="values")
    label = models.CharField(max_length=80)
    value = models.SlugField(max_length=80)
    color_hex = models.CharField(max_length=7, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "option", "value"], name="unique_option_value"
            )
        ]
        ordering = ["sort_order", "label"]


class OfferingVariant(TenantOwnedModel):
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=80)
    title = models.CharField(max_length=180, blank=True)
    option_values = models.ManyToManyField(OptionValue, blank=True, related_name="variants")
    price_override = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    stock_tracking_enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "sku"], name="unique_variant_sku_per_org"
            )
        ]
        indexes = [models.Index(fields=["organization", "offering"])]

    @property
    def price(self):
        return (
            self.price_override if self.price_override is not None else self.offering.display_price
        )

    def __str__(self) -> str:
        return self.title or self.sku


class OfferingImage(TenantOwnedModel):
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(
        OfferingVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="images",
    )
    asset = models.ForeignKey(
        "core.MediaAsset", on_delete=models.PROTECT, related_name="offering_images"
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order"]
