import base64

import pytest
from rest_framework.test import APIClient

from apps.accounts.services import register_user
from apps.devices.models import Device
from apps.devices.services import apply_wa_event
from apps.integrations.wa_gateway import WaGatewayClient
from apps.messaging.models import Message
from apps.workspaces.models import Workspace

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"


def _setup():
    user = register_user(email="dev@example.com", password=PASSWORD, full_name="Dev")
    workspace = Workspace.objects.get(owner=user)
    device = Device.objects.create(
        workspace=workspace, name="primary", status=Device.Status.CONNECTED
    )
    api = APIClient()
    login = api.post(
        "/v1/auth/login", {"email": "dev@example.com", "password": PASSWORD}, format="json"
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return workspace, device, api


def test_send_text_message(monkeypatch) -> None:
    workspace, device, api = _setup()
    monkeypatch.setattr(
        WaGatewayClient,
        "send_text",
        lambda self, device_id, to, body: {"waMessageId": "wamid.1"},
    )
    response = api.post(
        "/v1/messages/",
        {"device": str(device.id), "to": "15551234567", "text": "hi"},
        format="json",
    )
    assert response.status_code == 202
    assert response.data["status"] == Message.Status.SENT
    assert response.data["wa_message_id"] == "wamid.1"
    assert (
        Message.objects.filter(workspace=workspace, direction=Message.Direction.OUTBOUND).count()
        == 1
    )


def test_send_is_idempotent(monkeypatch) -> None:
    workspace, device, api = _setup()
    calls = {"n": 0}

    def fake_send(self, device_id, to, body):
        calls["n"] += 1
        return {"waMessageId": "wamid.X"}

    monkeypatch.setattr(WaGatewayClient, "send_text", fake_send)
    payload = {"device": str(device.id), "to": "1555", "text": "hi", "idempotency_key": "abc-123"}

    first = api.post("/v1/messages/", payload, format="json")
    second = api.post("/v1/messages/", payload, format="json")

    assert first.status_code == 202 and second.status_code == 202
    assert first.data["id"] == second.data["id"]
    assert calls["n"] == 1
    assert Message.objects.filter(workspace=workspace).count() == 1


def test_send_text_requires_text() -> None:
    _workspace, device, api = _setup()
    response = api.post(
        "/v1/messages/",
        {"device": str(device.id), "to": "1555", "type": "text"},
        format="json",
    )
    assert response.status_code == 400


def test_send_media_message(monkeypatch, settings, tmp_path) -> None:
    settings.MEDIA_ROOT = str(tmp_path)
    _workspace, device, api = _setup()
    monkeypatch.setattr(
        WaGatewayClient,
        "send_media",
        lambda self, device_id, to, **kwargs: {"waMessageId": "wamid.m"},
    )
    encoded = base64.b64encode(b"fake-image-bytes").decode()
    payload = {
        "device": str(device.id),
        "to": "1555",
        "type": "media",
        "media": {"mime_type": "image/png", "data_base64": encoded, "filename": "a.png"},
    }
    response = api.post("/v1/messages/", payload, format="json")
    assert response.status_code == 202
    assert response.data["message_type"] == Message.Type.IMAGE
    message = Message.objects.get(id=response.data["id"])
    assert message.media is not None


def test_send_to_unknown_device() -> None:
    _workspace, _device, api = _setup()
    response = api.post(
        "/v1/messages/",
        {"device": "00000000-0000-0000-0000-000000000000", "to": "1", "text": "x"},
        format="json",
    )
    assert response.status_code == 404


def test_inbound_message_persisted() -> None:
    workspace, device, _api = _setup()
    apply_wa_event(
        {
            "deviceId": str(device.id),
            "type": "message",
            "data": {
                "waMessageId": "in.1",
                "from": "1555@c.us",
                "body": "hello",
                "messageType": "chat",
            },
            "timestamp": "t",
        }
    )
    message = Message.objects.get(workspace=workspace, direction=Message.Direction.INBOUND)
    assert message.body == "hello"
    assert message.wa_message_id == "in.1"


def test_inbound_message_deduped() -> None:
    workspace, device, _api = _setup()
    event = {
        "deviceId": str(device.id),
        "type": "message",
        "data": {"waMessageId": "in.dup", "from": "1", "body": "x", "messageType": "chat"},
        "timestamp": "t",
    }
    apply_wa_event(event)
    apply_wa_event(event)
    assert (
        Message.objects.filter(
            workspace=workspace, direction=Message.Direction.INBOUND, wa_message_id="in.dup"
        ).count()
        == 1
    )


def test_list_messages() -> None:
    workspace, device, api = _setup()
    Message.objects.create(
        workspace=workspace,
        device=device,
        direction=Message.Direction.OUTBOUND,
        message_type=Message.Type.TEXT,
        address="1",
        body="a",
        status=Message.Status.SENT,
    )
    response = api.get("/v1/messages/")
    assert response.status_code == 200
    assert response.data["pagination"]["count"] == 1
    assert len(response.data["results"]) == 1
