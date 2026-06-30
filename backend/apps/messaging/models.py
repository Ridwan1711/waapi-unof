"""Message log (inbound + outbound) and media assets.

Media is written through the swappable storage backend (local now, S3 later).
Every message is scoped to a workspace and a device, and may reference a
:class:`MediaAsset`. The optional ``idempotency_key`` prevents duplicate sends
on client retries (unique per workspace when present).
"""

from __future__ import annotations

from django.db import models

from apps.core.models import BaseModel
from apps.core.storage import get_media_storage


class MediaAsset(BaseModel):
    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="media_assets"
    )
    file = models.FileField(upload_to="wa/%Y/%m/%d/", storage=get_media_storage)
    mime_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA-256 hex digest")
    original_filename = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.original_filename or str(self.id)


class Message(BaseModel):
    class Direction(models.TextChoices):
        INBOUND = "in", "Inbound"
        OUTBOUND = "out", "Outbound"

    class Type(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        DOCUMENT = "document", "Document"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        STICKER = "sticker", "Sticker"
        LOCATION = "location", "Location"
        CONTACT = "contact", "Contact"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"
        RECEIVED = "received", "Received"

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="messages"
    )
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=3, choices=Direction.choices)
    message_type = models.CharField(max_length=16, choices=Type.choices, default=Type.TEXT)
    chat_id = models.CharField(max_length=128, blank=True, help_text="WhatsApp chat/JID")
    address = models.CharField(
        max_length=64, blank=True, help_text="Recipient (outbound) or sender (inbound)"
    )
    body = models.TextField(blank=True)
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.QUEUED)
    wa_message_id = models.CharField(max_length=255, blank=True, db_index=True)
    error = models.TextField(blank=True)
    idempotency_key = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "-created_at"]),
            models.Index(fields=["device", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="uniq_idempotency_key_per_workspace",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_direction_display()} {self.message_type} {self.address}".strip()
