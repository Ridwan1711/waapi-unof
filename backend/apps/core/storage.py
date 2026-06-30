"""Storage helper.

Media is written through Django's configured ``STORAGES["default"]`` backend.
Today that is the local filesystem; migrating to S3 later only requires changing
the ``STORAGES`` setting (e.g. to ``storages.backends.s3.S3Storage``) — no
model or business-logic changes. Model ``FileField``s should call
:func:`get_media_storage` so the backend stays swappable in one place.
"""

from __future__ import annotations

from django.core.files.storage import Storage, storages


def get_media_storage() -> Storage:
    return storages["default"]
