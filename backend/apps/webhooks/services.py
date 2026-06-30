"""Webhook fan-out and delivery.

`emit_event` records a delivery per subscribed webhook and enqueues dispatch.
`attempt_delivery` performs one HMAC-signed POST and updates the delivery state,
returning whether a retry should be scheduled (exponential backoff).
"""

from __future__ import annotations

import json
import logging
import time
from datetime import timedelta

import httpx
from django.utils import timezone

from apps.core.signing import make_signature

from .models import Webhook, WebhookDelivery

logger = logging.getLogger(__name__)

_MAX_BACKOFF_SECONDS = 3600
_REQUEST_TIMEOUT_SECONDS = 10.0
_RESPONSE_SNIPPET_LIMIT = 2000


def backoff_seconds(attempts: int) -> int:
    return min(2**attempts * 10, _MAX_BACKOFF_SECONDS)


def emit_event(workspace, event_type: str, payload: dict) -> list[WebhookDelivery]:
    """Create + enqueue a delivery for every active webhook subscribed to the event.

    A webhook with an empty `events` list is treated as subscribed to all events.
    """
    deliveries: list[WebhookDelivery] = []
    for webhook in Webhook.objects.filter(workspace=workspace, is_active=True):
        if webhook.events and event_type not in webhook.events:
            continue
        delivery = WebhookDelivery.objects.create(
            webhook=webhook, event_type=event_type, payload=payload
        )
        deliveries.append(delivery)
        # Imported here to avoid importing Celery tasks at module load.
        from .tasks import dispatch_webhook_delivery

        dispatch_webhook_delivery.delay(str(delivery.id))
    return deliveries


def attempt_delivery(delivery: WebhookDelivery) -> bool:
    """Perform one delivery attempt. Returns True if a retry should be scheduled."""
    webhook = delivery.webhook
    body = json.dumps({"event": delivery.event_type, "data": delivery.payload}).encode()
    timestamp = str(int(time.time() * 1000))
    headers = {
        "Content-Type": "application/json",
        "X-Signature": make_signature(webhook.secret, timestamp, body),
        "X-Timestamp": timestamp,
        "X-Webhook-Event": delivery.event_type,
    }

    delivery.attempts += 1
    try:
        response = httpx.post(
            webhook.url, content=body, headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        delivery.response_status = response.status_code
        delivery.response_body = (response.text or "")[:_RESPONSE_SNIPPET_LIMIT]
        if 200 <= response.status_code < 300:
            delivery.status = WebhookDelivery.Status.SUCCESS
            delivery.delivered_at = timezone.now()
            delivery.next_retry_at = None
            delivery.save()
            return False
    except httpx.HTTPError as exc:
        delivery.response_status = None
        delivery.response_body = str(exc)[:_RESPONSE_SNIPPET_LIMIT]

    if delivery.attempts >= delivery.max_attempts:
        delivery.status = WebhookDelivery.Status.DEAD
        delivery.next_retry_at = None
        delivery.save()
        return False

    delivery.status = WebhookDelivery.Status.RETRYING
    delivery.next_retry_at = timezone.now() + timedelta(seconds=backoff_seconds(delivery.attempts))
    delivery.save()
    return True
