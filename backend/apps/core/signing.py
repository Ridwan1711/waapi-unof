"""HMAC signing shared by the Django <-> Node internal channel.

Signature = HMAC_SHA256(secret, f"{timestamp}." + body). This must stay
byte-for-byte identical to the Node implementation in
`wa-service/src/utils/signing.ts`.
"""

from __future__ import annotations

import hashlib
import hmac
import time

DEFAULT_MAX_SKEW_MS = 5 * 60 * 1000


def make_signature(secret: str, timestamp: str, body: bytes) -> str:
    message = f"{timestamp}.".encode() + body
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def verify_signature(
    secret: str,
    timestamp: str | None,
    signature: str | None,
    body: bytes,
    *,
    max_skew_ms: int = DEFAULT_MAX_SKEW_MS,
) -> bool:
    if not timestamp or not signature:
        return False
    try:
        age = abs(int(time.time() * 1000) - int(timestamp))
    except (TypeError, ValueError):
        return False
    if age > max_skew_ms:
        return False
    expected = make_signature(secret, timestamp, body)
    return hmac.compare_digest(expected, signature)
