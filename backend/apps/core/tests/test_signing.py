import time

from apps.core.signing import make_signature, verify_signature

SECRET = "test-secret"


def _now_ms() -> str:
    return str(int(time.time() * 1000))


def test_round_trip() -> None:
    ts = _now_ms()
    body = b'{"a":1}'
    signature = make_signature(SECRET, ts, body)
    assert verify_signature(SECRET, ts, signature, body)


def test_rejects_tampered_body() -> None:
    ts = _now_ms()
    signature = make_signature(SECRET, ts, b'{"a":1}')
    assert not verify_signature(SECRET, ts, signature, b'{"a":2}')


def test_rejects_wrong_secret() -> None:
    ts = _now_ms()
    body = b"payload"
    signature = make_signature(SECRET, ts, body)
    assert not verify_signature("other-secret", ts, signature, body)


def test_rejects_stale_timestamp() -> None:
    stale = str(int(time.time() * 1000) - 10 * 60 * 1000)
    body = b"payload"
    signature = make_signature(SECRET, stale, body)
    assert not verify_signature(SECRET, stale, signature, body)


def test_rejects_missing_parts() -> None:
    assert not verify_signature(SECRET, None, None, b"")
