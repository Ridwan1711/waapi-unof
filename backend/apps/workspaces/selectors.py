from __future__ import annotations

from django.db.models import QuerySet

from .models import Workspace


def get_user_workspaces(user) -> QuerySet[Workspace]:
    return Workspace.objects.filter(memberships__user=user).distinct()


def get_active_workspace(request) -> Workspace | None:
    """Resolve the workspace for the current request.

    - API-key requests are bound to the key's workspace.
    - JWT/session users use their first workspace (multi-workspace switching via
      a header is a later enhancement).
    """
    # Imported lazily to avoid a circular import with the apikeys app.
    from apps.apikeys.models import ApiKey

    auth = getattr(request, "auth", None)
    if isinstance(auth, ApiKey):
        return auth.workspace

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return get_user_workspaces(user).first()
    return None
