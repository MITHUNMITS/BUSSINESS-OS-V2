from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from business_os.apps.core.models import RecordStatus, TenantOwnedModel, TimeStampedModel


class Website(TimeStampedModel):
    organization = models.OneToOneField(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="website",
    )
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=180)
    template_pack = models.CharField(max_length=80, default="fashion_editorial")
    default_locale = models.CharField(max_length=16, default="en")
    primary_domain = models.CharField(max_length=180, blank=True)
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
    )
    published_version = models.PositiveIntegerField(default=0)
    powered_by_visible = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class WebsiteTheme(TenantOwnedModel):
    website = models.OneToOneField(Website, on_delete=models.CASCADE, related_name="theme")
    style_name = models.CharField(max_length=80, default="fashion")
    tokens = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.website} theme"


class WebsitePage(TenantOwnedModel):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="pages")
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=180)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_homepage = models.BooleanField(default=False)
    required_capability = models.SlugField(max_length=120, blank=True)
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["website", "slug"], name="unique_page_slug_per_website")
        ]
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title


class WebsiteSection(TenantOwnedModel):
    page = models.ForeignKey(WebsitePage, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=80)
    variant = models.CharField(max_length=80, default="default")
    content = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    required_capability = models.SlugField(max_length=120, blank=True)

    class Meta:
        ordering = ["sort_order"]
        indexes = [models.Index(fields=["organization", "section_type"])]


class WebsiteVersion(TenantOwnedModel):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    snapshot = models.JSONField(default=dict)
    published_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_website_versions",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["website", "version_number"],
                name="unique_website_version_number",
            )
        ]

