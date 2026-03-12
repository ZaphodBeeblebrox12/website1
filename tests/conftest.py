"""
Pytest configuration for community platform.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile
from apps.audit.models import AuditLog

User = get_user_model()


@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def factory(**kwargs):
        defaults = {
            "telegram_id": 123456789,
            "telegram_username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }
        defaults.update(kwargs)
        user = User.objects.create(**defaults)
        Profile.objects.create(user=user)
        return user
    return factory


@pytest.fixture
def admin_user(user_factory):
    """Create an admin user."""
    return user_factory(
        telegram_id=999999999,
        telegram_username="admin",
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
        is_staff_approved=True,
    )


@pytest.fixture
def staff_user(user_factory):
    """Create a staff user pending approval."""
    return user_factory(
        telegram_id=888888888,
        telegram_username="staff",
        role=User.Role.STAFF,
        is_staff=False,
        is_staff_approved=False,
    )


@pytest.fixture
def banned_user(user_factory):
    """Create a banned user."""
    user = user_factory(
        telegram_id=777777777,
        telegram_username="banned",
    )
    user.ban("Test ban reason")
    return user


@pytest.fixture
def telegram_auth_data():
    """Sample Telegram auth data for testing."""
    return {
        "id": 123456789,
        "auth_date": 1704067200,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "photo_url": "https://t.me/i/userpic/320/test.jpg",
    }
