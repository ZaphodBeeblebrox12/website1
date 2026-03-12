"""
Django admin configuration for accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    """Inline profile for user admin."""
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ["timezone", "language", "avatar_url"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with ban controls and staff approval."""

    inlines = [ProfileInline]

    list_display = [
        "username",
        "telegram_username",
        "telegram_id",
        "full_name",
        "role",
        "is_staff_approved",
        "is_banned",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "role",
        "is_staff_approved",
        "is_banned",
        "is_active",
        "date_joined",
    ]
    search_fields = [
        "username",
        "telegram_username",
        "telegram_id",
        "first_name",
        "last_name",
        "email",
    ]
    readonly_fields = [
        "id",
        "date_joined",
        "last_login",
        "banned_at",
    ]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Telegram"), {"fields": ("telegram_id", "telegram_username")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "role",
                    "is_staff_approved",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Ban Status"),
            {
                "fields": ("is_banned", "ban_reason", "banned_at"),
                "classes": ("collapse",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "telegram_id", "telegram_username", "role", "password1", "password2"),
            },
        ),
    )

    ordering = ["-date_joined"]

    actions = ["approve_staff", "ban_users", "unban_users"]

    @admin.action(description="Approve selected staff users")
    def approve_staff(self, request, queryset):
        """Approve staff role for selected users."""
        count = 0
        for user in queryset.filter(role="staff", is_staff_approved=False):
            user.approve_staff()
            count += 1
        self.message_user(request, f"Approved {count} staff users.")

    @admin.action(description="Ban selected users")
    def ban_users(self, request, queryset):
        """Ban selected users."""
        count = 0
        for user in queryset.filter(is_banned=False):
            user.ban("Banned via admin action")
            count += 1
        self.message_user(request, f"Banned {count} users.")

    @admin.action(description="Unban selected users")
    def unban_users(self, request, queryset):
        """Unban selected users."""
        count = 0
        for user in queryset.filter(is_banned=True):
            user.unban()
            count += 1
        self.message_user(request, f"Unbanned {count} users.")

    def full_name(self, obj):
        """Display full name."""
        return obj.full_name
    full_name.short_description = "Name"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile admin."""
    list_display = ["user", "timezone", "language", "created_at"]
    list_filter = ["timezone", "language"]
    search_fields = ["user__username", "user__telegram_username"]
