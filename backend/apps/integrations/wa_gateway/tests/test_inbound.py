import json
import time

import pytest

from apps.accounts.models import User
from apps.core.signing import make_signature
from apps.devices.models import Device
from apps.workspaces.models import Workspace

pytestmark = pytest.mark.django_db

EVENTS_URL = "/internal/events"


def _signed_headers(secret: str, body: bytes) -> dict[str, str]:
    ts = str(int(time.time() * 1000))
    return {"x-timestamp": ts, "x-signature": make_signature(secret, ts, body)}


def _make_device() -> Device:
    user = User.objects.create_user(email="owner@example.com", password="pw-12345")
    workspace = Workspace.objects.create(name="Acme", slug="acme", owner=user)
    return Device.objects.create(workspace=workspace, name="primary")


def test_rejects_missing_signature(client) -> None:
    response = client.post(EVENTS_URL, data=b"{}", content_type="application/json")
    assert response.status_code == 401


def test_rejects_invalid_signature(client) -> None:
    body = b'{"type":"qr"}'
    headers = {"x-timestamp": str(int(time.time() * 1000)), "x-signature": "deadbeef"}
    response = client.post(EVENTS_URL, data=body, content_type="application/json", headers=headers)
    assert response.status_code == 401


def test_accepts_valid_event_and_updates_device(client, settings) -> None:
    device = _make_device()
    payload = {
        "deviceId": str(device.id),
        "type": "ready",
        "data": {"phone": "15551234567"},
        "timestamp": "2026-01-01T00:00:00Z",
    }
    body = json.dumps(payload).encode()
    headers = _signed_headers(settings.INTERNAL_API_SECRET, body)

    response = client.post(EVENTS_URL, data=body, content_type="application/json", headers=headers)

    assert response.status_code == 202
    device.refresh_from_db()
    assert device.status == Device.Status.CONNECTED
    assert device.phone_number == "15551234567"
