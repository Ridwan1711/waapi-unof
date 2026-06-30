import pytest
from rest_framework.test import APIClient

from apps.accounts.services import register_user
from apps.automation.models import AutoReplyRule
from apps.automation.services import _matches, handle_inbound_auto_reply
from apps.devices.models import Device
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


def test_matches_variants() -> None:
    M = AutoReplyRule.Match
    assert _matches(
        AutoReplyRule(match_type=M.CONTAINS, pattern="hi", case_sensitive=False), "say HI"
    )
    assert _matches(AutoReplyRule(match_type=M.EXACT, pattern="ping", case_sensitive=False), "PING")
    assert _matches(
        AutoReplyRule(match_type=M.STARTS_WITH, pattern="hel", case_sensitive=False), "Hello"
    )
    assert _matches(
        AutoReplyRule(match_type=M.REGEX, pattern=r"\d{3}", case_sensitive=False), "code 123"
    )
    assert not _matches(
        AutoReplyRule(match_type=M.CONTAINS, pattern="bye", case_sensitive=False), "hi"
    )
    # Invalid regex must not raise.
    assert not _matches(AutoReplyRule(match_type=M.REGEX, pattern="[", case_sensitive=False), "x")


def test_auto_reply_sends_on_match(monkeypatch) -> None:
    workspace, device, _api = _setup()
    AutoReplyRule.objects.create(
        workspace=workspace,
        name="greet",
        match_type=AutoReplyRule.Match.CONTAINS,
        pattern="hi",
        response_body="Hello!",
        is_active=True,
        priority=10,
    )
    monkeypatch.setattr(
        WaGatewayClient, "send_text", lambda self, device_id, to, body: {"waMessageId": "wamid.r"}
    )

    rule = handle_inbound_auto_reply(device, "15550001111@c.us", "hi there")

    assert rule is not None
    outbound = Message.objects.filter(workspace=workspace, direction=Message.Direction.OUTBOUND)
    assert outbound.count() == 1
    assert outbound.first().body == "Hello!"


def test_auto_reply_no_match(monkeypatch) -> None:
    workspace, device, _api = _setup()
    AutoReplyRule.objects.create(
        workspace=workspace,
        name="greet",
        match_type=AutoReplyRule.Match.CONTAINS,
        pattern="hi",
        response_body="Hello!",
    )
    monkeypatch.setattr(
        WaGatewayClient, "send_text", lambda self, device_id, to, body: {"waMessageId": "x"}
    )

    rule = handle_inbound_auto_reply(device, "1@c.us", "goodbye")

    assert rule is None
    assert Message.objects.filter(direction=Message.Direction.OUTBOUND).count() == 0


def test_autoreply_crud() -> None:
    _workspace, _device, api = _setup()
    created = api.post(
        "/v1/auto-reply-rules/",
        {"name": "r1", "match_type": "contains", "pattern": "hi", "response_body": "hello"},
        format="json",
    )
    assert created.status_code == 201
    rule_id = created.data["id"]

    assert len(api.get("/v1/auto-reply-rules/").data) == 1

    patched = api.patch(f"/v1/auto-reply-rules/{rule_id}", {"is_active": False}, format="json")
    assert patched.status_code == 200
    assert patched.data["is_active"] is False

    assert api.delete(f"/v1/auto-reply-rules/{rule_id}").status_code == 204
