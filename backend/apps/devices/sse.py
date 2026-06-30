"""Server-Sent Events streaming for device QR + status.

The Node service publishes events to the Redis channel `wa:events:<deviceId>`;
this module relays them to the browser as an SSE stream.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator

import redis
from django.conf import settings

from .models import Device

_PING_INTERVAL_SECONDS = 15


def sse_format(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def iter_device_events(device: Device) -> Iterator[str]:
    # Immediately send the current snapshot so the client renders without delay.
    yield sse_format(
        "status",
        {"deviceId": str(device.id), "status": device.status, "phone": device.phone_number},
    )

    if not settings.REDIS_URL:
        # No realtime backend configured; the snapshot is all we can provide.
        return

    client = redis.from_url(settings.REDIS_URL)
    pubsub = client.pubsub()
    pubsub.subscribe(f"wa:events:{device.id}")
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
