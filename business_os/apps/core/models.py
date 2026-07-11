from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class RecordStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    PENDING = "pending", _("Pending")
    HIDDEN = "hidden", _("Hidden")
    SUSPENDED = "suspended", _("Suspended")
    ARCHIVED = "archived", _("Archived")
    DELETED = "deleted", _("Deleted")


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantQuerySet(models.QuerySet):
    def for_organization(self, organization: Any) -> TenantQuerySet:
        organization_id = getattr(organization, "id", organization)
        return self.filter(organization_id=organization_id)

    def for_facility(self, facility: Any) -> TenantQuerySet:
        facility_id = getattr(facility, "id", facility)
        return self.filter(facility_id=facility_id)

    def active(self) -> TenantQuerySet:
        return self.filter(status=RecordStatus.ACTIVE)


class TenantOwnedModel(TimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )
    facility = models.ForeignKey(
        "organizations.Facility",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_set",
    )
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    objects = TenantQuerySet.as_manager()

    class Meta:
        abstract = True


class AuditEvent(TimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    facility = models.ForeignKey(
        "organizations.Facility",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=160, db_index=True)
    target_type = models.CharField(max_length=160, blank=True)
    target_id = models.CharField(max_length=80, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=80, blank=True, db_index=True)
    reason = models.CharField(max_length=255, blank=True)
    support_mode = models.BooleanField(default=False)
    source = models.CharField(max_length=80, default="web")

    class Meta:
        indexes = [
            models.Index(fields=["organization", "action", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} {self.target_type}:{self.target_id}"


class MediaAsset(TenantOwnedModel):
    class AccessLevel(models.TextChoices):
        PUBLIC = "public", _("Public")
        TENANT = "tenant", _("Tenant")
        PRIVATE = "private", _("Private")

    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="tenant-media/%Y/%m/")
    mime_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    access_level = models.CharField(
        max_length=24,
        choices=AccessLevel.choices,
        default=AccessLevel.TENANT,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "access_level"]),
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title
