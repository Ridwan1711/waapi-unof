from __future__ import annotations

import secrets

from django.db import transaction
from django.utils.text import slugify

from apps.workspaces.models import Membership, Workspace

from .models import User


def _unique_workspace_slug(seed: str) -> str:
    base = slugify(seed.split("@")[0]) or "workspace"
    slug = base
    while Workspace.objects.filter(slug=slug).exists():
        slug = f"{base}-{secrets.token_hex(3)}"
    return slug


@transaction.atomic
def register_user(*, email: str, password: str, full_name: str = "") -> User:
    """Create a user plus a default workspace they own (team-ready from day one)."""
    user = User.objects.create_user(email=email, password=password, full_name=full_name)
    workspace = Workspace.objects.create(
        name=f"{full_name or email.split('@')[0]}'s workspace",
        slug=_unique_workspace_slug(email),
        owner=user,
    )
    Membership.objects.create(workspace=workspace, user=user, role=Membership.Role.OWNER)
    return user
