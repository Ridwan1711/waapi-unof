"""Consistent API error envelope.

All DRF errors are reshaped into:

    {"error": {"code": "...", "message": "...", "details": {...}}}

so clients can rely on a single, documented error format (see docs/api.md).
"""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    response = drf_exception_handler(exc, context)
    if response is None:
        # Unhandled (non-DRF) exception: let Django's handler deal with it.
        return None

    default_code = getattr(exc, "default_code", None) or "error"
    data = response.data
    details: dict[str, Any] = {}

    if isinstance(data, dict) and "detail" in data:
        message = str(data["detail"])
        code = getattr(data["detail"], "code", default_code)
    elif isinstance(data, dict):
        message = "Validation failed."
        code = default_code
        details = data
    elif isinstance(data, list):
        message = "Validation failed."
        code = default_code
        details = {"non_field_errors": data}
    else:
        message = str(data)
        code = default_code

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
