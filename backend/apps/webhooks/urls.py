from __future__ import annotations

from django.urls import path

from .views import WebhookDeliveryListView, WebhookDetailView, WebhookListCreateView

urlpatterns = [
    path("", WebhookListCreateView.as_view(), name="webhook-list-create"),
    path("<uuid:pk>", WebhookDetailView.as_view(), name="webhook-detail"),
    path("<uuid:pk>/deliveries", WebhookDeliveryListView.as_view(), name="webhook-deliveries"),
]
