"""Scheduled (and future recurring) messages.

A one-off send is dispatched via Celery with an ``eta`` of ``run_at``. The
optional ``recurrence`` field holds an iCal RRULE string for future recurring
schedules. The denormalized ``payload`` captures exactly what to send.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class ScheduledMessage(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="scheduled_messages"
    )
    device = models.ForeignKey(
        "devices.Device", on_delete=models.CASCADE, related_name="scheduled_messages"
    )
    payload = models.JSONField(default=dict, help_text="{to, type, body, media_id, ...}")
    run_at = models.DateTimeField(db_index=True)
    recurrence = models.CharField(
        max_length=255, blank=True, help_text="iCal RRULE for recurring sends (optional)"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    celery_task_id = models.CharField(max_length=255, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["run_at"]
        indexes = [models.Index(fields=["status", "run_at"])]

    def __str__(self) -> str:
        return f"Scheduled {self.run_at:%Y-%m-%d %H:%M} ({self.status})"
