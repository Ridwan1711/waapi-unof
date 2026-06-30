"""Auto-reply rules.

When an inbound message arrives, rules for the device (or workspace-wide rules
where ``device`` is null) are evaluated in ``priority`` order; the first match
produces an automatic reply. Matching is performed in the service layer.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class AutoReplyRule(BaseModel):
    class Match(models.TextChoices):
        EXACT = "exact", "Exact"
        CONTAINS = "contains", "Contains"
        STARTS_WITH = "starts_with", "Starts with"
        REGEX = "regex", "Regex"

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="auto_reply_rules"
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="auto_reply_rules",
        help_text="Leave empty to apply to all devices in the workspace.",
    )
    name = models.CharField(max_length=255)
    match_type = models.CharField(max_length=12, choices=Match.choices, default=Match.CONTAINS)
    pattern = models.CharField(max_length=512)
    case_sensitive = models.BooleanField(default=False)
    response_body = models.TextField()
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher numbers are evaluated first.")

    class Meta:
        ordering = ["-priority", "created_at"]

    def __str__(self) -> str:
        return self.name
