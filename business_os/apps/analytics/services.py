from __future__ import annotations

from business_os.apps.analytics.models import AnalyticsEvent


def track_event(
    *,
    organization,
    event_type: str,
    facility=None,
    subject_type: str = "",
    subject_id: str = "",
    metadata: dict | None = None,
) -> AnalyticsEvent:
    return AnalyticsEvent.objects.create(
        organization=organization,
        facility=facility,
        event_type=event_type,
        subject_type=subject_type,
        subject_id=subject_id,
        metadata=metadata or {},
    )

