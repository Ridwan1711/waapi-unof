from __future__ import annotations

from django.urls import path

from .views import (
    ScheduledMessageCancelView,
    ScheduledMessageDetailView,
    ScheduledMessageListCreateView,
)

urlpatterns = [
    path("", ScheduledMessageListCreateView.as_view(), name="scheduled-list-create"),
    path("<uuid:pk>", ScheduledMessageDetailView.as_view(), name="scheduled-detail"),
    path("<uuid:pk>/cancel", ScheduledMessageCancelView.as_view(), name="scheduled-cancel"),
]
