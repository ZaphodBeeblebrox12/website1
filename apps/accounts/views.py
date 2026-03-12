"""
Views for accounts app with VERBOSE DEBUG logging.
"""
import logging
from django.contrib.auth import login
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.audit.models import AuditLog
from integrations.telegram.auth import parse_telegram_auth_data, verify_telegram_auth_hash

from .models import Profile, User
from .serializers import (
    BanUserSerializer,
    StaffApprovalSerializer,
    TelegramAuthSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


def generate_username_from_telegram(data: dict) -> str:
    """Generate a unique username from Telegram data."""
    telegram_id = data.get("id")
    username = data.get("username", "")

    if username:
        base_username = f"tg_{username}"
    else:
        base_username = f"tg_{telegram_id}"

    # Ensure uniqueness
    counter = 0
    final_username = base_username
    while User.objects.filter(username=final_username).exists():
        counter += 1
        final_username = f"{base_username}_{counter}"

    return final_username


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def telegram_auth(request: HttpRequest) -> Response:
    """
    Handle Telegram Login Widget authentication with VERBOSE logging.
    """
    logger.info("=" * 80)
    logger.info("TELEGRAM AUTH REQUEST RECEIVED")
    logger.info("=" * 80)
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"Request POST data: {request.POST}")
    logger.info(f"Request body: {request.body}")

    # Try to get data from POST or JSON
    data = request.data if hasattr(request, 'data') else request.POST
    logger.info(f"Data received: {data}")

    serializer = TelegramAuthSerializer(data=data)
    if not serializer.is_valid():
        logger.error(f"SERIALIZER ERRORS: {serializer.errors}")
        return Response(
            {"error": "Invalid data", "details": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    logger.info(f"Validated data: {validated_data}")

    # Verify hash
    from django.conf import settings
    logger.info(f"TELEGRAM_BOT_TOKEN configured: {bool(settings.TELEGRAM_BOT_TOKEN)}")
    logger.info(f"TELEGRAM_BOT_TOKEN length: {len(settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else 0}")

    hash_valid = verify_telegram_auth_hash(validated_data, settings.TELEGRAM_BOT_TOKEN)
    logger.info(f"Hash verification result: {hash_valid}")

    if not hash_valid:
        logger.error("HASH VERIFICATION FAILED!")
        logger.error(f"Received hash: {validated_data.get('hash')}")
        return Response(
            {"error": "Invalid authentication hash"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Parse auth data
    auth_data = parse_telegram_auth_data(validated_data)
    logger.info(f"Parsed auth data: id={auth_data.id}, username={auth_data.username}, auth_date={auth_data.auth_date}")

    # Try to find existing user by telegram_id
    logger.info(f"Looking for existing user with telegram_id={auth_data.id}")
    try:
        user = User.objects.get(telegram_id=auth_data.id)
        created = False
        logger.info(f"FOUND EXISTING USER: {user.username} (ID: {user.id})")
        # Update user info
        user.telegram_username = auth_data.username
        user.first_name = auth_data.first_name
        user.last_name = auth_data.last_name
        user.save()
        logger.info("Updated user info from Telegram")
    except User.DoesNotExist:
        logger.info(f"NO EXISTING USER FOUND with telegram_id={auth_data.id}")
        # Create new user with auto-generated username
        username = generate_username_from_telegram(validated_data)
        logger.info(f"Generated new username: {username}")

        try:
            user = User.objects.create(
                username=username,
                telegram_id=auth_data.id,
                telegram_username=auth_data.username,
                first_name=auth_data.first_name,
                last_name=auth_data.last_name,
            )
            logger.info(f"CREATED NEW USER: {user.username} (ID: {user.id})")
            # Create profile for new user
            Profile.objects.create(
                user=user,
                avatar_url=auth_data.photo_url,
            )
            logger.info("Created user profile")
            created = True
        except Exception as e:
            logger.error(f"ERROR CREATING USER: {str(e)}")
            return Response(
                {"error": f"Failed to create user: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Check if banned
    if user.is_banned:
        logger.warning(f"BANNED USER ATTEMPTED LOGIN: {user.username}")
        return Response(
            {"error": "Account is banned"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Log the user in
    logger.info(f"Logging in user: {user.username}")
    login(request, user)

    # Log audit event
    AuditLog.objects.create(
        user=user,
        action="user_created" if created else "user_login",
        object_type="User",
        object_id=str(user.id),
        metadata={
            "telegram_id": auth_data.id,
            "username": auth_data.username,
            "auth_date": auth_data.auth_date,
        }
    )

    logger.info(f"AUTH SUCCESSFUL for user: {user.username}")
    logger.info("=" * 80)

    return Response({
        "success": True,
        "user": UserSerializer(user).data,
        "created": created,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request: HttpRequest) -> Response:
    """Get current authenticated user."""
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def staff_approvals_list(request: HttpRequest) -> Response:
    """List pending staff approvals."""
    pending_staff = User.objects.filter(
        role=User.Role.STAFF,
        is_staff_approved=False
    )
    return Response(UserSerializer(pending_staff, many=True).data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def staff_approval_action(request: HttpRequest) -> Response:
    """Approve or reject a staff user."""
    serializer = StaffApprovalSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = serializer.validated_data["user_id"]
    action = serializer.validated_data["action"]

    try:
        user = User.objects.get(id=user_id, role=User.Role.STAFF)
    except User.DoesNotExist:
        return Response(
            {"error": "Staff user not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if action == "approve":
        user.approve_staff()
        AuditLog.objects.create(
            user=request.user,
            action="staff_approved",
            object_type="User",
            object_id=str(user.id),
            metadata={"approved_user": str(user.id)}
        )
        return Response({"status": "approved", "user": UserSerializer(user).data})
    else:
        user.role = User.Role.USER
        user.save()
        AuditLog.objects.create(
            user=request.user,
            action="staff_rejected",
            object_type="User",
            object_id=str(user.id),
            metadata={"rejected_user": str(user.id)}
        )
        return Response({"status": "rejected", "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def ban_user(request: HttpRequest) -> Response:
    """Ban a user."""
    serializer = BanUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = serializer.validated_data["user_id"]
    reason = serializer.validated_data.get("reason", "")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if user.is_admin:
        return Response(
            {"error": "Cannot ban admin users"},
            status=status.HTTP_403_FORBIDDEN
        )

    user.ban(reason)

    AuditLog.objects.create(
        user=request.user,
        action="user_banned",
        object_type="User",
        object_id=str(user.id),
        metadata={"reason": reason}
    )

    return Response({"status": "banned", "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def unban_user(request: HttpRequest) -> Response:
    """Unban a user."""
    user_id = request.data.get("user_id")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    user.unban()

    AuditLog.objects.create(
        user=request.user,
        action="user_unbanned",
        object_type="User",
        object_id=str(user.id),
        metadata={}
    )

    return Response({"status": "unbanned", "user": UserSerializer(user).data})
