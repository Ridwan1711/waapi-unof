"""Root URL configuration.

Public, versioned API routes are mounted under ``/v1/`` and are added by each
feature app in later phases. This module wires the always-on infrastructure
endpoints: health checks, the OpenAPI schema, Swagger UI, and the admin.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import health_check, readiness_check
from apps.integrations.wa_gateway.views import WaEventsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("health/ready/", readiness_check, name="readiness"),
    # Internal channel (HMAC-authenticated) — called by the Node WA service.
    path("internal/events", WaEventsView.as_view(), name="wa-events"),
    # Public, versioned API.
    path("v1/auth/", include("apps.accounts.urls")),
    path("v1/api-keys/", include("apps.apikeys.urls")),
    path("v1/devices/", include("apps.devices.urls")),
    path("v1/messages/", include("apps.messaging.urls")),
    path("v1/webhooks/", include("apps.webhooks.urls")),
    path("v1/scheduled-messages/", include("apps.scheduler.urls")),
    path("v1/auto-reply-rules/", include("apps.automation.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]

# Feature routers are appended here per phase, e.g.:
#   path("v1/auth/", include("apps.accounts.urls")),

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
