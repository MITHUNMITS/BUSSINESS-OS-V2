from django.contrib import admin

from business_os.apps.core.models import AuditEvent, MediaAsset


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "organization", "actor", "target_type", "target_id", "created_at")
    list_filter = ("action", "support_mode", "source")
    search_fields = ("action", "target_type", "target_id", "request_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "access_level", "mime_type", "created_at")
    list_filter = ("access_level", "mime_type")
    search_fields = ("title", "alt_text")

