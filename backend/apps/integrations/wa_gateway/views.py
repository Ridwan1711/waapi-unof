"""Inbound endpoint for signed events from the Node WhatsApp service."""

from __future__ import annotations

import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.core.signing import verify_signature
from apps.devices.services import apply_wa_event


@method_decorator(csrf_exempt, name="dispatch")
class WaEventsView(View):
    """POST /internal/events — receives qr/ready/disconnected/message events.

    Authenticated by HMAC (not JWT/API key); only the Node service, which shares
    INTERNAL_API_SECRET, can call it. Real-time fan-out to the dashboard (SSE)
    and message persistence build on this in later phases.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        signature = request.headers.get("x-signature")
        timestamp = request.headers.get("x-timestamp")
        if not verify_signature(settings.INTERNAL_API_SECRET, timestamp, signature, request.body):
            return JsonResponse(
                {"error": {"code": "unauthorized", "message": "Invalid signature."}},
                status=401,
            )

        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": {"code": "bad_request", "message": "Invalid JSON."}},
                status=400,
            )

        apply_wa_event(payload)
        return JsonResponse({"status": "accepted"}, status=202)
