from __future__ import annotations

from django.urls import path

from .views import MessageDetailView, MessageListCreateView

urlpatterns = [
    path("", MessageListCreateView.as_view(), name="message-list-create"),
    path("<uuid:pk>", MessageDetailView.as_view(), name="message-detail"),
]
