"""Typed client for the Node WhatsApp service.

Every request is HMAC-signed (see apps.core.signing). This is the *only* way the
platform talks to the Node service; business code calls these methods, never
HTTP directly.
"""

from __future__ import annotations

import json
import time
from typing import Any

import httpx
from django.conf import settings

from apps.core.signing import make_signature

from .exceptions import WaGatewayError


class WaGatewayClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        secret: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = (base_url or settings.WA_SERVICE_INTERNAL_URL).rstrip("/")
        self.secret = secret or settings.INTERNAL_API_SECRET
        self.timeout = timeout

    def _headers(self, body: bytes) -> dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        return {
            "Content-Type": "application/json",
            "x-timestamp": timestamp,
            "x-signature": make_signature(self.secret, timestamp, body),
        }

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode() if payload is not None else b""
        try:
            response = httpx.request(
                method,
                f"{self.base_url}{path}",
                content=body,
                headers=self._headers(body),
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise WaGatewayError(f"WA service request failed: {exc}") from exc
        if response.status_code >= 400:
            raise WaGatewayError(f"WA service returned {response.status_code}: {response.text}")
        return response.json() if response.content else {}

    def init_session(self, device_id: str) -> dict[str, Any]:
        return self._request("POST", "/internal/sessions", {"deviceId": str(device_id)})

    def get_status(self, device_id: str) -> dict[str, Any]:
        return self._request("GET", f"/internal/devices/{device_id}/status")

    def send_text(self, device_id: str, to: str, body: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/internal/devices/{device_id}/send",
            {"type": "text", "to": to, "body": body},
        )

    def send_media(
        self,
        device_id: str,
        to: str,
        *,
        mime_type: str,
        data_base64: str,
        filename: str | None = None,
        caption: str | None = None,
    ) -> dict[str, Any]:
        media: dict[str, str] = {"mimeType": mime_type, "dataBase64": data_base64}
        if filename:
            media["filename"] = filename
        if caption:
            media["caption"] = caption
        return self._request(
            "POST",
            f"/internal/devices/{device_id}/send",
            {"type": "media", "to": to, "media": media},
        )

    def logout(self, device_id: str) -> dict[str, Any]:
        return self._request("POST", f"/internal/devices/{device_id}/logout", {})
