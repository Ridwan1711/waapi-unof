from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle

from .models import ApiKey


class ApiKeyRateThrottle(SimpleRateThrottle):
    """Per-key rate limiting using each key's own ``rate_limit_per_min``.

    Non-API-key requests (e.g. JWT) are not throttled by this class.
    """

    scope = "api_key"

    def get_rate(self) -> str | None:
        # Rate is determined per-key at request time (see allow_request).
        return None

    def allow_request(self, request, view) -> bool:
        api_key = getattr(request, "auth", None)
        if not isinstance(api_key, ApiKey):
            return True

        self.key = f"throttle_api_key_{api_key.pk}"
        self.num_requests = max(1, api_key.rate_limit_per_min)
        self.duration = 60
        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def get_cache_key(self, request, view) -> str | None:
        return None
