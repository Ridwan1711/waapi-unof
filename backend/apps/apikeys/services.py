from __future__ import annotations

import hashlib
import secrets

from .models import ApiKey

_PREFIX_BYTES = 4
_SECRET_BYTES = 32


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def generate_api_key(
    *,
    workspace,
    name: str,
    scopes: list[str] | None = None,
    created_by=None,
    rate_limit_per_min: int = 120,
) -> tuple[ApiKey, str]:
    """Create an API key and return (instance, raw_key).

    The raw key (``prefix.secret``) is returned once and never stored; only the
    SHA-256 hash of the secret is persisted.
    """
    prefix = secrets.token_hex(_PREFIX_BYTES)
    while ApiKey.objects.filter(prefix=prefix).exists():
        prefix = secrets.token_hex(_PREFIX_BYTES)

    secret = secrets.token_urlsafe(_SECRET_BYTES)
    api_key = ApiKey.objects.create(
        workspace=workspace,
        name=name,
        prefix=prefix,
        hashed_key=hash_secret(secret),
        scopes=scopes or [],
        created_by=created_by,
        rate_limit_per_min=rate_limit_per_min,
    )
    return api_key, f"{prefix}.{secret}"
