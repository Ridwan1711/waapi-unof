"""Outbound webhooks.

A :class:`Webhook` is a customer-registered endpoint subscribed to a set of
event types. Each delivery attempt is recorded as a :class:`WebhookDelivery`,
enabling at-least-once delivery with exponential backoff and an auditable
history. Payloads are HMAC-signed with the webhook ``secret``.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class Webhook(BaseModel):
    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="webhooks"
    )
    url = models.URLField(max_length=2048)
    secret = models.CharField(max_length=255)
    events = models.JSONField(
        default=list, blank=True, help_text="Subscribed event types, e.g. ['message.in']"
    )
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.url


class WebhookDelivery(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"
        DEAD = "dead", "Dead (max attempts reached)"

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "next_retry_at"])]

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.webhook_id} ({self.status})"
