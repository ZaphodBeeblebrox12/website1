"""
Admin configuration for audit logs.
"""
from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log admin - read only."""
    list_display = [
        "created_at",
        "action",
        "user",
        "object_type",
        "object_id",
    ]
    list_filter = ["action", "object_type", "created_at"]
    search_fields = ["user__telegram_username", "action", "object_id"]
    readonly_fields = [
        "id",
        "user",
        "action",
        "object_type",
        "object_id",
        "metadata",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
