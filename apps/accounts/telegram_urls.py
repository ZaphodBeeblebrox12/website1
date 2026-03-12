"""
URL configuration for Telegram web login widget page.
"""
from django.urls import path

from .telegram_views import telegram_login_page
from .debug_views import debug_telegram_config

urlpatterns = [
    path("", telegram_login_page, name="telegram-login-page"),
    path("debug/", debug_telegram_config, name="telegram-debug"),
]
