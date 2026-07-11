from __future__ import annotations

from django.db import models
from django.utils import timezone

from business_os.apps.core.models import TenantOwnedModel


class AnalyticsEvent(TenantOwnedModel):
    event_type = models.CharField(max_length=120, db_index=True)
    subject_type = models.CharField(max_length=120, blank=True)
    subject_id = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "event_type", "occurred_at"]),
            models.Index(fields=["subject_type", "subject_id"]),
        ]

