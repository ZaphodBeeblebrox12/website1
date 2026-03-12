"""
Production settings for community platform.
"""
from .base import *  # noqa: F403, F401

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Logging
LOGGING["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": BASE_DIR / "logs" / "django.log",
    "maxBytes": 1024 * 1024 * 5,  # 5 MB
    "backupCount": 5,
    "formatter": "verbose",
}
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]
