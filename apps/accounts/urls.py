"""
URL configuration for accounts app (public auth endpoints).
"""
from django.urls import path

from .views import current_user, telegram_auth

urlpatterns = [
    path("telegram/", telegram_auth, name="telegram-auth"),
    path("me/", current_user, name="current-user"),
]
