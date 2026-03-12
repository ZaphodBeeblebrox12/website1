"""
Debug view to check Telegram settings
"""
from django.conf import settings
from django.http import JsonResponse


def debug_telegram_config(request):
    """Debug endpoint to check Telegram configuration."""
    return JsonResponse({
        'TELEGRAM_BOT_USERNAME': getattr(settings, 'TELEGRAM_BOT_USERNAME', 'NOT SET'),
        'TELEGRAM_BOT_TOKEN_CONFIGURED': bool(settings.TELEGRAM_BOT_TOKEN),
        'TELEGRAM_BOT_TOKEN_PREFIX': settings.TELEGRAM_BOT_TOKEN.split(':')[0] if settings.TELEGRAM_BOT_TOKEN else 'NOT SET',
    })
