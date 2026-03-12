"""
Views for Telegram web login widget.
"""
from django.conf import settings
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)


def telegram_login_page(request):
    """Render Telegram login widget page."""
    # PRIORITY 1: Use TELEGRAM_BOT_USERNAME from settings
    bot_name = getattr(settings, 'TELEGRAM_BOT_USERNAME', '')

    # PRIORITY 2: If not set, try to extract from token
    if not bot_name and settings.TELEGRAM_BOT_TOKEN:
        if ':' in settings.TELEGRAM_BOT_TOKEN:
            potential_name = settings.TELEGRAM_BOT_TOKEN.split(':')[0]
            # Only use if it's NOT all digits (i.e., it's a username, not numeric ID)
            if not potential_name.isdigit():
                bot_name = potential_name

    # Check if we have a valid bot name
    has_error = not bool(bot_name)

    # Debug logging
    logger.info(f"TELEGRAM_BOT_USERNAME from settings: {getattr(settings, 'TELEGRAM_BOT_USERNAME', 'NOT SET')}")
    logger.info(f"TELEGRAM_BOT_TOKEN starts with: {settings.TELEGRAM_BOT_TOKEN[:20] if settings.TELEGRAM_BOT_TOKEN else 'NOT SET'}...")
    logger.info(f"Final bot_name for template: {bot_name}")

    return render(request, "accounts/telegram_login.html", {
        "telegram_bot_name": bot_name,
        "error": has_error,
    })
