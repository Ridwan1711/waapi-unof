"""Scheduling business logic."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.messaging.models import Message
from apps.messaging.services import send_message

from .models import ScheduledMessage

logger = logging.getLogger(__name__)


def create_scheduled_message(
    *, workspace, device, run_at, payload: dict[str, Any]
) -> ScheduledMessage:
    scheduled = ScheduledMessage.objects.create(
        workspace=workspace,
        device=device,
        run_at=run_at,
        payload=payload,
        status=ScheduledMessage.Status.PENDING,
    )
    # Imported here to avoid importing Celery tasks at module load.
    from .tasks import send_scheduled_message

    result = send_scheduled_message.apply_async((str(scheduled.id),), eta=run_at)
    scheduled.celery_task_id = getattr(result, "id", "") or ""
    scheduled.status = ScheduledMessage.Status.QUEUED
    scheduled.save(update_fields=["celery_task_id", "status", "updated_at"])
    return scheduled


def run_scheduled_message(scheduled: ScheduledMessage) -> None:
    if scheduled.status == ScheduledMessage.Status.CANCELLED:
        return
    payload = scheduled.payload or {}
    message = send_message(
        device=scheduled.device,
        to=payload.get("to", ""),
        message_type=payload.get("type", "text"),
        text=payload.get("text", ""),
        media=payload.get("media"),
    )
    scheduled.status = (
        ScheduledMessage.Status.SENT
        if message.status == Message.Status.SENT
        else ScheduledMessage.Status.FAILED
    )
    scheduled.last_run_at = timezone.now()
    scheduled.save(update_fields=["status", "last_run_at", "updated_at"])


def cancel_scheduled_message(scheduled: ScheduledMessage) -> ScheduledMessage:
    if scheduled.celery_task_id:
        try:
            from config.celery import app

            app.control.revoke(scheduled.celery_task_id)
        except Exception:  # best-effort: broker may be unavailable
            logger.warning("failed to revoke task %s", scheduled.celery_task_id)
    scheduled.status = ScheduledMessage.Status.CANCELLED
    scheduled.save(update_fields=["status", "updated_at"])
    return scheduled
