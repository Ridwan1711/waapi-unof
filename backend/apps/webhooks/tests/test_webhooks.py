import json

import httpx
import pytest
from rest_framework.test import APIClient

from apps.accounts.services import register_user
from apps.core.signing import verify_signature
from apps.webhooks import services, tasks
from apps.webhooks.models import Webhook, WebhookDelivery
from apps.workspaces.models import Workspace

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"
SECRET = "whsecret"


class FakeResponse:
    def __init__(self, status_code: int, text: str = "ok") -> None:
        self.status_code = status_code
        self.text = text


def _workspace() -> Workspace:
    user = register_user(email="dev@example.com", password=PASSWORD, full_name="Dev")
    return Workspace.objects.get(owner=user)


def _webhook(workspace, **kwargs) -> Webhook:
    defaults = {
        "url": "https://example.com/hook",
        "secret": SECRET,
        "events": [],
        "is_active": True,
    }
    defaults.update(kwargs)
    return Webhook.objects.create(workspace=workspace, **defaults)


def _delivery(webhook, **kwargs) -> WebhookDelivery:
    return WebhookDelivery.objects.create(
        webhook=webhook, event_type="message.received", payload={"hello": "world"}, **kwargs
    )


def _jwt_client() -> APIClient:
    register_user(email="owner@example.com", password=PASSWORD, full_name="Owner")
    api = APIClient()
    login = api.post(
        "/v1/auth/login", {"email": "owner@example.com", "password": PASSWORD}, format="json"
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return api


def test_attempt_delivery_success_signs_payload(monkeypatch) -> None:
    delivery = _delivery(_webhook(_workspace()))
    captured: dict = {}

    def fake_post(url, *, content, headers, timeout):
        captured["content"] = content
        captured["headers"] = headers
        return FakeResponse(200)

    monkeypatch.setattr(httpx, "post", fake_post)

    should_retry = services.attempt_delivery(delivery)

    assert should_retry is False
    delivery.refresh_from_db()
    assert delivery.status == WebhookDelivery.Status.SUCCESS
    assert delivery.delivered_at is not None
    # The signature must verify with the webhook secret.
    headers = captured["headers"]
    assert verify_signature(
        SECRET, headers["X-Timestamp"], headers["X-Signature"], captured["content"]
    )
    assert json.loads(captured["content"])["event"] == "message.received"


def test_attempt_delivery_schedules_retry(monkeypatch) -> None:
    delivery = _delivery(_webhook(_workspace()))
    monkeypatch.setattr(httpx, "post", lambda url, **kw: FakeResponse(500, "err"))

    should_retry = services.attempt_delivery(delivery)

    assert should_retry is True
    delivery.refresh_from_db()
    assert delivery.status == WebhookDelivery.Status.RETRYING
    assert delivery.attempts == 1
    assert delivery.next_retry_at is not None


def test_attempt_delivery_dead_after_max(monkeypatch) -> None:
    delivery = _delivery(_webhook(_workspace()), max_attempts=1)
    monkeypatch.setattr(httpx, "post", lambda url, **kw: FakeResponse(500, "err"))

    should_retry = services.attempt_delivery(delivery)

    assert should_retry is False
    delivery.refresh_from_db()
    assert delivery.status == WebhookDelivery.Status.DEAD


def test_attempt_delivery_handles_transport_error(monkeypatch) -> None:
    delivery = _delivery(_webhook(_workspace()))

    def boom(url, **kwargs):
        raise httpx.ConnectError("unreachable")

    monkeypatch.setattr(httpx, "post", boom)

    should_retry = services.attempt_delivery(delivery)
    assert should_retry is True
    delivery.refresh_from_db()
    assert delivery.status == WebhookDelivery.Status.RETRYING


def test_emit_event_only_for_subscribers(monkeypatch) -> None:
    workspace = _workspace()
    _webhook(workspace, events=["message.received"])
    _webhook(workspace, events=["device.connected"])
    monkeypatch.setattr(tasks.dispatch_webhook_delivery, "delay", lambda *a, **k: None)

    deliveries = services.emit_event(workspace, "message.received", {"x": 1})

    assert len(deliveries) == 1
    assert WebhookDelivery.objects.count() == 1


def test_dispatch_task_invokes_attempt(monkeypatch) -> None:
    delivery = _delivery(_webhook(_workspace()))
    called = {"n": 0}

    def fake_attempt(d):
        called["n"] += 1
        return False

    monkeypatch.setattr(tasks, "attempt_delivery", fake_attempt)
    tasks.dispatch_webhook_delivery.apply(args=[str(delivery.id)])
    assert called["n"] == 1


def test_webhook_crud() -> None:
    api = _jwt_client()

    created = api.post(
        "/v1/webhooks/",
        {"url": "https://example.com/hook", "events": ["message.received"]},
        format="json",
    )
    assert created.status_code == 201
    assert created.data["secret"]  # generated server-side
    webhook_id = created.data["id"]

    assert len(api.get("/v1/webhooks/").data) == 1

    patched = api.patch(f"/v1/webhooks/{webhook_id}", {"is_active": False}, format="json")
    assert patched.status_code == 200
    assert patched.data["is_active"] is False

    assert api.get(f"/v1/webhooks/{webhook_id}/deliveries").status_code == 200
    assert api.delete(f"/v1/webhooks/{webhook_id}").status_code == 204
