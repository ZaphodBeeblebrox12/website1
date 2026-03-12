"""
Admin configuration for system settings.
"""
from django.contrib import admin

from .models import SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """System setting admin."""
    list_display = ["key", "value_preview", "is_public", "updated_at"]
    list_filter = ["is_public"]
    search_fields = ["key", "value", "description"]
    readonly_fields = ["created_at", "updated_at"]

    def value_preview(self, obj):
        """Show truncated value."""
        if len(obj.value) > 50:
            return obj.value[:50] + "..."
        return obj.value
    value_preview.short_description = "Value"
