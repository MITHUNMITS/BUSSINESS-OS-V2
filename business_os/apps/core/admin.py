from django.contrib import admin

from business_os.apps.core.models import (
    AuditEvent,
    MediaAsset,
    PlatformRole,
    PlatformRoleAssignment,
    SupportSession,
)


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "organization",
        "actor",
        "target_type",
        "target_id",
        "support_mode",
        "created_at",
    )
    list_filter = ("action", "support_mode", "source")
    search_fields = ("action", "target_type", "target_id", "request_id", "reason")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlatformRole)
class PlatformRoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_system", "is_active", "created_at")
    list_filter = ("is_system", "is_active")
    search_fields = ("code", "name", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlatformRoleAssignment)
class PlatformRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "starts_at", "expires_at", "revoked_at")
    list_filter = ("role", "revoked_at")
    search_fields = ("user__username", "user__email", "role__code", "reason")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SupportSession)
class SupportSessionAdmin(admin.ModelAdmin):
    list_display = ("actor", "organization", "scope", "started_at", "expires_at", "ended_at")
    list_filter = ("scope", "ended_at")
    search_fields = ("actor__username", "actor__email", "organization__name", "reason")
    readonly_fields = ("created_at", "updated_at")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "access_level", "mime_type", "created_at")
    list_filter = ("access_level", "mime_type")
    search_fields = ("title", "alt_text")
