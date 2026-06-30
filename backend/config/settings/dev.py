"""Development settings: relaxed, developer-friendly."""

from __future__ import annotations

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Allow the local frontend dev server out of the box.
CORS_ALLOW_ALL_ORIGINS = True

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
