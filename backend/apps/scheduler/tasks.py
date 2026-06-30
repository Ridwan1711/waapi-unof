from __future__ import annotations

from celery import shared_task

from .models import ScheduledMessage
from .services import run_scheduled_message


@shared_task(ignore_result=True)
def send_scheduled_message(scheduled_id: str) -> None:
    scheduled = ScheduledMessage.objects.filter(id=scheduled_id).first()
    if scheduled is None:
        return
    run_scheduled_message(scheduled)
