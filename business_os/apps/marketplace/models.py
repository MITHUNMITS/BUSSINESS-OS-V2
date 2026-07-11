from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import TimeStampedModel


class ReleaseStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    INTERNAL = "internal", _("Internal")
    PRIVATE_BETA = "private_beta", _("Private beta")
    PUBLIC = "public", _("Public")
    DEPRECATED = "deprecated", _("Deprecated")
    RETIRED = "retired", _("Retired")


class Module(TimeStampedModel):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, db_index=True)
    icon = models.CharField(max_length=80, default="box")
    benefits = models.JSONField(default=list, blank=True)
    navigation = models.JSONField(default=list, blank=True)
    website_contributions = models.JSONField(default=list, blank=True)
    dashboard_widgets = models.JSONField(default=list, blank=True)
    supported_countries = models.JSONField(default=list, blank=True)
    supported_industries = models.JSONField(default=list, blank=True)
    release_status = models.CharField(
        max_length=32,
        choices=ReleaseStatus.choices,
        default=ReleaseStatus.DRAFT,
        db_index=True,
    )
    visible_in_marketplace = models.BooleanField(default=False)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name


class Capability(TimeStampedModel):
    code = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    default_limit = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class ModuleCapability(TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="module_capabilities")
    capability = models.ForeignKey(
        Capability, on_delete=models.CASCADE, related_name="module_links"
    )
    included = models.BooleanField(default=True)
    required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["module", "capability"], name="unique_module_capability"
            )
        ]
        ordering = ["sort_order", "capability__code"]


class ModuleDependency(TimeStampedModel):
    class DependencyType(models.TextChoices):
        REQUIRED = "required", _("Required")
        OPTIONAL = "optional", _("Optional")
        RECOMMENDED = "recommended", _("Recommended")
        CONFLICTING = "conflicting", _("Conflicting")

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="dependencies")
    depends_on = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="dependent_modules"
    )
    dependency_type = models.CharField(
        max_length=32,
        choices=DependencyType.choices,
        default=DependencyType.REQUIRED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["module", "depends_on", "dependency_type"],
                name="unique_module_dependency",
            )
        ]


class ModulePrice(TimeStampedModel):
    class PricingType(models.TextChoices):
        FIXED_RECURRING = "fixed_recurring", _("Fixed recurring")
        ANNUAL_RECURRING = "annual_recurring", _("Annual recurring")
        ONE_TIME = "one_time", _("One-time")
        USAGE_BASED = "usage_based", _("Usage-based")
        MANUAL = "manual", _("Manual enterprise")

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="prices")
    capability = models.ForeignKey(
        Capability,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="prices",
    )
    country = models.CharField(max_length=2, blank=True)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_period = models.CharField(max_length=20, default="monthly")
    pricing_type = models.CharField(
        max_length=32,
        choices=PricingType.choices,
        default=PricingType.FIXED_RECURRING,
    )
    active = models.BooleanField(default=True)
    tax_inclusive = models.BooleanField(default=False)
    snapshot_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["module", "country", "currency", "active"])]


class ModuleLimit(TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="limits")
    capability = models.ForeignKey(
        Capability,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="limits",
    )
    code = models.SlugField(max_length=120)
    included_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=40)
    overage_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["module", "code"], name="unique_module_limit_code")
        ]


class Bundle(TimeStampedModel):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    supported_countries = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.name


class BundleItem(TimeStampedModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name="items")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="bundle_items")
    capability = models.ForeignKey(
        Capability,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bundle_items",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bundle", "module", "capability"],
                name="unique_bundle_module_capability",
            )
        ]
