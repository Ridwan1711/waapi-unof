"""Messaging business logic: outbound sends and inbound persistence."""

from __future__ import annotations

import base64
import logging
from typing import Any

from django.core.files.base import ContentFile

from apps.integrations.wa_gateway import WaGatewayClient, WaGatewayError

from .models import MediaAsset, Message

logger = logging.getLogger(__name__)

# Map whatsapp-web.js message types to our Message.Type values.
_WA_TYPE_MAP = {
    "chat": Message.Type.TEXT,
    "image": Message.Type.IMAGE,
    "video": Message.Type.VIDEO,
    "audio": Message.Type.AUDIO,
    "ptt": Message.Type.AUDIO,
    "document": Message.Type.DOCUMENT,
    "sticker": Message.Type.STICKER,
    "location": Message.Type.LOCATION,
    "vcard": Message.Type.CONTACT,
}


def _media_type_from_mime(mime: str) -> str:
    mime = (mime or "").lower()
    if mime.startswith("image/"):
        return Message.Type.IMAGE
    if mime.startswith("video/"):
        return Message.Type.VIDEO
    if mime.startswith("audio/"):
        return Message.Type.AUDIO
    return Message.Type.DOCUMENT


def _store_media(workspace, media: dict[str, Any]) -> MediaAsset:
    raw = base64.b64decode(media["data_base64"])
    asset = MediaAsset(
        workspace=workspace,
        mime_type=media.get("mime_type", ""),
        size=len(raw),
        original_filename=media.get("filename", "") or "",
    )
    asset.file.save(media.get("filename") or "upload.bin", ContentFile(raw), save=True)
    return asset


def send_message(
    *,
    device,
    to: str,
    message_type: str = "text",
    text: str = "",
    media: dict[str, Any] | None = None,
    idempotency_key: str = "",
) -> Message:
    """Persist an outbound message and dispatch it via the Node gateway.

    Idempotent: re-sending with the same key returns the original message
    instead of dispatching again.
    """
    workspace = device.workspace
    if idempotency_key:
        existing = Message.objects.filter(
            workspace=workspace, idempotency_key=idempotency_key
        ).first()
        if existing is not None:
            return existing

    media_asset = _store_media(workspace, media) if message_type == "media" and media else None
    resolved_type = (
        Message.Type.TEXT
        if message_type == "text"
        else _media_type_from_mime(media.get("mime_type", "") if media else "")
    )
    message = Message.objects.create(
        workspace=workspace,
        device=device,
        direction=Message.Direction.OUTBOUND,
        message_type=resolved_type,
        address=to,
        body=text,
        media=media_asset,
        status=Message.Status.QUEUED,
        idempotency_key=idempotency_key,
    )

    client = WaGatewayClient()
    try:
        if message_type == "text":
            result = client.send_text(str(device.id), to, text)
        else:
            assert media is not None  # guaranteed by serializer validation
            result = client.send_media(
                str(device.id),
                to,
                mime_type=media["mime_type"],
                data_base64=media["data_base64"],
                filename=media.get("filename") or None,
                caption=media.get("caption") or None,
            )
        message.wa_message_id = str(result.get("waMessageId", ""))
        message.status = Message.Status.SENT
    except WaGatewayError as exc:
        logger.warning("send failed for device %s: %s", device.id, exc)
        message.status = Message.Status.FAILED
        message.error = str(exc)

    message.save(update_fields=["wa_message_id", "status", "error", "updated_at"])
    return message


def persist_inbound_message(device, data: dict[str, Any]) -> None:
    """Store an inbound message event from the Node service (deduped by id)."""
    wa_message_id = str(data.get("waMessageId") or "")
    if (
        wa_message_id
        and Message.objects.filter(
            workspace=device.workspace,
            wa_message_id=wa_message_id,
            direction=Message.Direction.INBOUND,
        ).exists()
    ):
        return

    message = Message.objects.create(
        workspace=device.workspace,
        device=device,
        direction=Message.Direction.INBOUND,
        message_type=_WA_TYPE_MAP.get(str(data.get("messageType") or ""), Message.Type.TEXT),
        address=str(data.get("from") or ""),
        body=str(data.get("body") or ""),
        wa_message_id=wa_message_id,
        status=Message.Status.RECEIVED,
    )

    # Notify subscribed webhooks. Imported lazily to avoid a circular import.
    from apps.webhooks.services import emit_event

    emit_event(
        device.workspace,
        "message.received",
        {
            "message_id": str(message.id),
            "device_id": str(device.id),
            "from": message.address,
            "body": message.body,
            "type": message.message_type,
            "wa_message_id": message.wa_message_id,
        },
    )

    # Evaluate auto-reply rules (best-effort). Imported lazily to avoid a cycle.
    from apps.automation.services import handle_inbound_auto_reply

    handle_inbound_auto_reply(device, message.address, message.body)
