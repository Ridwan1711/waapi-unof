from __future__ import annotations

from django.urls import path

from .views import ApiKeyListCreateView, ApiKeyRevokeView

urlpatterns = [
    path("", ApiKeyListCreateView.as_view(), name="apikey-list-create"),
    path("<uuid:pk>/revoke", ApiKeyRevokeView.as_view(), name="apikey-revoke"),
]
