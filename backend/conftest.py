import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset the cache between tests so throttle counters don't leak across them."""
    cache.clear()
    yield
    cache.clear()
