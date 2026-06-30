from __future__ import annotations

import hmac

from django.utils import timezone
from rest_framework import authentication, exceptions

from .models import ApiKey
from .services import hash_secret

_TOUCH_INTERVAL_SECONDS = 60


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate requests bearing ``Authorization: Api-Key <prefix>.<secret>``.

    On success the request is bound to the key's workspace owner (so DRF sees an
    authenticated user) and ``request.auth`` is the :class:`ApiKey` itself, which
    carries the workspace and scopes.
    """

    keyword = "Api-Key"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].decode().lower() != self.keyword.lower():
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Invalid Api-Key header.")

        try:
            prefix, secret = header[1].decode().split(".", 1)
        except ValueError as exc:
            raise exceptions.AuthenticationFailed("Malformed API key.") from exc

        try:
            key = ApiKey.objects.select_related("workspace", "created_by").get(prefix=prefix)
        except ApiKey.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Invalid API key.") from exc

        if key.revoked_at is not None:
            raise exceptions.AuthenticationFailed("API key has been revoked.")
        if not hmac.compare_digest(key.hashed_key, hash_secret(secret)):
            raise exceptions.AuthenticationFailed("Invalid API key.")

        self._touch(key)
        return (key.created_by or key.workspace.owner, key)

    def authenticate_header(self, request) -> str:
        return self.keyword

    @staticmethod
    def _touch(key: ApiKey) -> None:
        now = timezone.now()
        if (
            key.last_used_at is None
            or (now - key.last_used_at).total_seconds() > _TOUCH_INTERVAL_SECONDS
        ):
            key.last_used_at = now
            key.save(update_fields=["last_used_at"])
