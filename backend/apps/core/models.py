"""Abstract base models reused across the project.

Every domain model inherits :class:`BaseModel`, giving it a non-sequential UUID
primary key (safe to expose in URLs/APIs) plus created/updated timestamps.
"""

from __future__ import annotations

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """UUID primary key + created/updated timestamps."""

    class Meta:
        abstract = True
