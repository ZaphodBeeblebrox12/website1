"""
Custom user manager for community platform.
"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager supporting both username and Telegram auth."""

    def create_user(self, username=None, password=None, **extra_fields):
        """Create and save a regular user."""
        if not username:
            # Auto-generate username from telegram_id or email if available
            if extra_fields.get("telegram_id"):
                username = f"tg_{extra_fields['telegram_id']}"
            elif extra_fields.get("email"):
                username = extra_fields["email"].split("@")[0]
            else:
                raise ValueError(_("User must have a username or telegram_id/email"))

        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff_approved", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Get user by username for authentication."""
        return self.get(username=username)
