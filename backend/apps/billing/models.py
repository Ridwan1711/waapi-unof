"""Foundation for future billing.

These models are intentionally minimal but real, so the data model is ready for
plans/usage metering without a migration upheaval later. No billing logic is
wired up yet; that arrives post-MVP.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class Plan(BaseModel):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="USD")
    limits = models.JSONField(
        default=dict, blank=True, help_text="e.g. {devices: 1, messages_per_month: 1000}"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_cents"]

    def __str__(self) -> str:
        return self.name


class Subscription(BaseModel):
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        CANCELLED = "cancelled", "Cancelled"

    workspace = models.OneToOneField(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.TRIALING)
    current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.workspace_id} · {self.plan_id} ({self.status})"
