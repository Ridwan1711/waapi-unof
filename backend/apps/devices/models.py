"""A Device represents one connected WhatsApp session.

The actual session lives in the Node WA service; this row tracks its identity,
lifecycle status, and which worker currently hosts it (for the session
registry). The ``provider`` field records which engine backs the session,
keeping the platform engine-agnostic (whatsapp-web.js today, Baileys later).
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel


class Device(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        INITIALIZING = "initializing", "Initializing"
        QR = "qr", "Awaiting QR scan"
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        FAILED = "failed", "Failed"
        LOGGED_OUT = "logged_out", "Logged out"

    class Provider(models.TextChoices):
        WWEBJS = "wwebjs", "whatsapp-web.js"
        BAILEYS = "baileys", "Baileys"

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="devices"
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.WWEBJS)
    worker_id = models.CharField(max_length=128, blank=True)
    session_ref = models.CharField(max_length=255, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "name"], name="uniq_device_name_per_workspace"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"
