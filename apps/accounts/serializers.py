"""
Serializers for accounts app.
"""
from rest_framework import serializers

from apps.accounts.models import User


class TelegramAuthSerializer(serializers.Serializer):
    """Serializer for Telegram authentication data."""
    id = serializers.IntegerField()
    auth_date = serializers.IntegerField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    hash = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.CharField(source="full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "telegram_id",
            "telegram_username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "role",
            "is_staff_approved",
            "is_banned",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "telegram_id",
            "is_staff_approved",
            "is_banned",
            "date_joined",
        ]


class StaffApprovalSerializer(serializers.Serializer):
    """Serializer for staff approval."""
    user_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=["approve", "reject"])


class BanUserSerializer(serializers.Serializer):
    """Serializer for banning a user."""
    user_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True)
