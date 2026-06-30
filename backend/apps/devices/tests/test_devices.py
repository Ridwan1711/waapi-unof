import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.services import register_user
from apps.devices.models import Device
from apps.devices.sse import sse_format
from apps.integrations.wa_gateway import WaGatewayClient, WaGatewayError
from apps.workspaces.models import Workspace

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"
RANDOM_UUID = "00000000-0000-0000-0000-000000000000"


def _setup():
    user = register_user(email="dev@example.com", password=PASSWORD, full_name="Dev")
    workspace = Workspace.objects.get(owner=user)
    api = APIClient()
    login = api.post(
        "/v1/auth/login",
        {"email": "dev@example.com", "password": PASSWORD},
        format="json",
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return user, workspace, api


def test_create_device_initializes_session(monkeypatch) -> None:
    user, workspace, api = _setup()
    monkeypatch.setattr(
        WaGatewayClient,
        "init_session",
        lambda self, device_id: {"deviceId": device_id, "status": "initializing"},
    )
    response = api.post("/v1/devices/", {"name": "primary"}, format="json")
    assert response.status_code == 201
    assert response.data["status"] == Device.Status.INITIALIZING
    assert Device.objects.filter(workspace=workspace, name="primary").exists()


def test_create_device_marks_failed_on_gateway_error(monkeypatch) -> None:
    _user, _workspace, api = _setup()

    def boom(self, device_id):
        raise WaGatewayError("node unavailable")

    monkeypatch.setattr(WaGatewayClient, "init_session", boom)
    response = api.post("/v1/devices/", {"name": "primary"}, format="json")
    assert response.status_code == 201
    assert response.data["status"] == Device.Status.FAILED


def test_sse_requires_token(client) -> None:
    response = client.get(f"/v1/devices/{RANDOM_UUID}/events")
    assert response.status_code == 401


def test_sse_unknown_device_returns_404(client) -> None:
    user, _workspace, _api = _setup()
    token = str(AccessToken.for_user(user))
    response = client.get(f"/v1/devices/{RANDOM_UUID}/events?token={token}")
    assert response.status_code == 404


def test_sse_streams_events(client, monkeypatch) -> None:
    user, workspace, _api = _setup()
    device = Device.objects.create(workspace=workspace, name="streamed")
    token = str(AccessToken.for_user(user))

    monkeypatch.setattr(
        "apps.devices.views.iter_device_events",
        lambda dev: iter([sse_format("ready", {"deviceId": str(dev.id)})]),
    )

    response = client.get(f"/v1/devices/{device.id}/events?token={token}")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/event-stream")
    body = b"".join(response.streaming_content)
    assert b"ready" in body


def test_sse_format_helper() -> None:
    frame = sse_format("status", {"a": 1})
    assert frame.startswith("event: status")
    assert '"a": 1' in frame
    assert frame.endswith("\n\n")


def test_delete_device(monkeypatch) -> None:
    _user, workspace, api = _setup()
    monkeypatch.setattr(WaGatewayClient, "logout", lambda self, device_id: {"status": "logged_out"})
    device = Device.objects.create(workspace=workspace, name="to-delete")

    response = api.delete(f"/v1/devices/{device.id}")
    assert response.status_code == 204
    assert not Device.objects.filter(id=device.id).exists()


def test_logout_device(monkeypatch) -> None:
    _user, workspace, api = _setup()
    monkeypatch.setattr(WaGatewayClient, "logout", lambda self, device_id: {"status": "logged_out"})
    device = Device.objects.create(
        workspace=workspace, name="to-logout", status=Device.Status.CONNECTED
    )

    response = api.post(f"/v1/devices/{device.id}/logout")
    assert response.status_code == 200
    assert response.data["status"] == Device.Status.LOGGED_OUT


def test_connect_device(monkeypatch) -> None:
    _user, workspace, api = _setup()
    monkeypatch.setattr(
        WaGatewayClient,
        "init_session",
        lambda self, device_id: {"deviceId": device_id, "status": "initializing"},
    )
    device = Device.objects.create(
        workspace=workspace, name="to-connect", status=Device.Status.DISCONNECTED
    )

    response = api.post(f"/v1/devices/{device.id}/connect")
    assert response.status_code == 200
    assert response.data["status"] == Device.Status.INITIALIZING
