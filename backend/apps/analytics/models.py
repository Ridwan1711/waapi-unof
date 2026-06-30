"""Pre-aggregated daily usage counters per workspace.

Rolling counts up front keeps dashboard queries cheap at scale (no scanning the
full message log). A Celery task populates these in a later phase.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class DailyUsage(BaseModel):
    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="daily_usage"
    )
    date = models.DateField(db_index=True)
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    media_sent = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "date"], name="uniq_usage_per_day")
        ]

    def __str__(self) -> str:
        return f"{self.workspace_id} {self.date}"
