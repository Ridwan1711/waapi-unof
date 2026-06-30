"""Device business logic.

`create_device` starts a WhatsApp session via the Node gateway; `apply_wa_event`
reconciles device state from events the Node service sends back.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.integrations.wa_gateway import WaGatewayClient, WaGatewayError

from .models import Device

logger = logging.getLogger(__name__)

_STATUS_BY_EVENT = {
    "qr": Device.Status.QR,
    "ready": Device.Status.CONNECTED,
    "disconnected": Device.Status.DISCONNECTED,
}


def create_device(*, workspace, name: str, provider: str = Device.Provider.WWEBJS) -> Device:
    """Create a device and ask the Node service to start its session.

    The row is created first so it survives a transient gateway hiccup; the
    status reflects whether initialization started (`initializing`) or failed.
    """
    device = Device.objects.create(
        workspace=workspace,
        name=name,
        provider=provider,
        status=Device.Status.PENDING,
    )
    try:
        WaGatewayClient().init_session(str(device.id))
        device.status = Device.Status.INITIALIZING
    except WaGatewayError:
        logger.warning("WA gateway init_session failed for device %s", device.id)
        device.status = Device.Status.FAILED
    device.save(update_fields=["status", "updated_at"])
    return device


def logout_device(device: Device) -> Device:
    """Log the device out of WhatsApp (best-effort) and mark it logged out."""
    try:
        WaGatewayClient().logout(str(device.id))
    except WaGatewayError:
        logger.warning("WA gateway logout failed for device %s", device.id)
    device.status = Device.Status.LOGGED_OUT
    device.save(update_fields=["status", "updated_at"])
    return device


def delete_device(device: Device) -> None:
    """Tear down the session (best-effort) and delete the device record."""
    try:
        WaGatewayClient().logout(str(device.id))
    except WaGatewayError:
        logger.warning("WA gateway logout (pre-delete) failed for device %s", device.id)
    device.delete()


def apply_wa_event(payload: dict[str, Any]) -> None:
    device_id = payload.get("deviceId")
    event_type = payload.get("type")
    data = payload.get("data") or {}
    if not device_id:
        return

    try:
        device = Device.objects.get(id=device_id)
    except (Device.DoesNotExist, ValidationError):
        # Unknown or malformed device id — nothing to reconcile.
        return

    update_fields = ["last_seen_at", "updated_at"]

    new_status = _STATUS_BY_EVENT.get(event_type)
    if event_type == "state" and data.get("state") == "auth_failure":
        new_status = Device.Status.FAILED
    if new_status is not None:
        device.status = new_status
        update_fields.append("status")

    if event_type == "ready" and data.get("phone"):
        device.phone_number = str(data["phone"])
        update_fields.append("phone_number")

    if event_type == "message":
        # Imported lazily to avoid a circular import with the messaging app.
        from apps.messaging.services import persist_inbound_message

        persist_inbound_message(device, data)

    device.last_seen_at = timezone.now()
    device.save(update_fields=update_fields)
