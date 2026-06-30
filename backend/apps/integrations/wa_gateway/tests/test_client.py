import httpx

from apps.core.signing import verify_signature
from apps.integrations.wa_gateway.client import WaGatewayClient


class _FakeResponse:
    status_code = 202
    content = b'{"status":"accepted"}'
    text = ""

    def json(self) -> dict[str, str]:
        return {"status": "accepted"}


def test_client_signs_request(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_request(method, url, *, content=b"", headers=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["content"] = content
        captured["headers"] = headers
        return _FakeResponse()

    monkeypatch.setattr(httpx, "request", fake_request)

    client = WaGatewayClient(secret="s3cret", base_url="http://wa-service:8090")
    client.init_session("device-1")

    headers = captured["headers"]
    assert captured["url"] == "http://wa-service:8090/internal/sessions"
    # The signature the client produced must verify against the same secret/body,
    # which is exactly what the Node service does on receipt.
    assert verify_signature(
        "s3cret",
        headers["x-timestamp"],
        headers["x-signature"],
        captured["content"],
    )
