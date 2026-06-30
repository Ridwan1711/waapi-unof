"""Infrastructure endpoints (not part of the versioned public API)."""

from __future__ import annotations

from django.db import connection
from django.http import HttpRequest, JsonResponse


def health_check(request: HttpRequest) -> JsonResponse:
    """Liveness probe: returns 200 as long as the process is up.

    Used by the container ``HEALTHCHECK``.
    """
    return JsonResponse({"status": "ok"})


def readiness_check(request: HttpRequest) -> JsonResponse:
    """Readiness probe: verifies the database is reachable."""
    database_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 - any DB error means "not ready"
        database_ok = False

    payload = {"status": "ok" if database_ok else "degraded", "database": database_ok}
    return JsonResponse(payload, status=200 if database_ok else 503)
