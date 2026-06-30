"""Server-Sent Events streaming for device QR + status.

The Node service publishes events to the Redis channel `wa:events:<deviceId>`;
this module relays them to the browser as an SSE stream and, on connect, replays
the current QR so a freshly connected client doesn't wait for the next refresh.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator

import redis
from django.conf import settings

from apps.integrations.wa_gateway import WaGatewayClient, WaGatewayError

from .models import Device

_PING_INTERVAL_SECONDS = 15


def sse_format(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _qr_frame(device_id: str, qr: str) -> str:
    payload = {"deviceId": device_id, "type": "qr", "data": {"qr": qr}}
    return f"data: {json.dumps(payload)}\n\n"


def iter_device_events(device: Device) -> Iterator[str]:
    device_id = str(device.id)

    # Immediate snapshot so the client renders status without delay.
    yield sse_format(
        "status",
        {"deviceId": device_id, "status": device.status, "phone": device.phone_number},
    )

    # Replay the current QR (if the session is awaiting a scan) so the client
    # sees it immediately instead of waiting for the next QR refresh from Node.
    try:
        snapshot = WaGatewayClient().get_status(device_id)
        if snapshot.get("qr"):
            yield _qr_frame(device_id, snapshot["qr"])
    except WaGatewayError:
        pass

    if not settings.REDIS_URL:
        # No realtime backend configured; the snapshot is all we can provide.
        return

    client = redis.from_url(settings.REDIS_URL)
    pubsub = client.pubsub()
    pubsub.subscribe(f"wa:events:{device_id}")
    last_ping = time.time()
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                payload = message["data"]
                if isinstance(payload, bytes):
                    payload = payload.decode()
                yield f"data: {payload}\n\n"
            if time.time() - last_ping > _PING_INTERVAL_SECONDS:
                yield ": ping\n\n"  # comment frame keeps the connection alive
                last_ping = time.time()
    finally:
        try:
            pubsub.close()
        finally:
            client.close()
