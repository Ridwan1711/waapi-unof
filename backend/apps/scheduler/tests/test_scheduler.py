import datetime as dt

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.services import register_user
from apps.devices.models import Device
from apps.integrations.wa_gateway import WaGatewayClient
from apps.messaging.models import Message
from apps.scheduler import tasks
from apps.scheduler.models import ScheduledMessage
from apps.scheduler.services import run_scheduled_message
from apps.workspaces.models import Workspace

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"


class FakeAsyncResult:
    id = "task-123"


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


def test_create_scheduled_message(monkeypatch) -> None:
    _workspace, device, api = _setup()
    monkeypatch.setattr(
        tasks.send_scheduled_message, "apply_async", lambda *a, **k: FakeAsyncResult()
    )
    run_at = (timezone.now() + dt.timedelta(hours=1)).isoformat()

    response = api.post(
        "/v1/scheduled-messages/",
        {"device": str(device.id), "run_at": run_at, "to": "15551234567", "text": "later"},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["status"] == ScheduledMessage.Status.QUEUED
    assert response.data["celery_task_id"] == "task-123"


def test_create_rejects_past_run_at() -> None:
    _workspace, device, api = _setup()
    run_at = (timezone.now() - dt.timedelta(hours=1)).isoformat()
    response = api.post(
        "/v1/scheduled-messages/",
        {"device": str(device.id), "run_at": run_at, "to": "1", "text": "x"},
        format="json",
    )
    assert response.status_code == 400


def test_run_scheduled_message_sends(monkeypatch) -> None:
    workspace, device, _api = _setup()
    monkeypatch.setattr(
        WaGatewayClient, "send_text", lambda self, device_id, to, body: {"waMessageId": "wamid.s"}
    )
    scheduled = ScheduledMessage.objects.create(
        workspace=workspace,
        device=device,
        run_at=timezone.now(),
        payload={"to": "15551234567", "type": "text", "text": "hello"},
        status=ScheduledMessage.Status.QUEUED,
    )

    run_scheduled_message(scheduled)

    scheduled.refresh_from_db()
    assert scheduled.status == ScheduledMessage.Status.SENT
    assert (
        Message.objects.filter(workspace=workspace, direction=Message.Direction.OUTBOUND).count()
        == 1
    )


def test_cancel_scheduled_message() -> None:
    workspace, device, api = _setup()
    scheduled = ScheduledMessage.objects.create(
        workspace=workspace,
        device=device,
        run_at=timezone.now(),
        payload={"to": "1", "type": "text", "text": "x"},
        status=ScheduledMessage.Status.QUEUED,
        celery_task_id="",
    )
    response = api.post(f"/v1/scheduled-messages/{scheduled.id}/cancel", format="json")
    assert response.status_code == 200
    assert response.data["status"] == ScheduledMessage.Status.CANCELLED
