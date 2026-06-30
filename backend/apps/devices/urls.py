from __future__ import annotations

from django.urls import path

from .views import (
    DeviceDetailView,
    DeviceEventsView,
    DeviceListCreateView,
    DeviceLogoutView,
)

urlpatterns = [
    path("", DeviceListCreateView.as_view(), name="device-list-create"),
    path("<uuid:pk>", DeviceDetailView.as_view(), name="device-detail"),
    path("<uuid:pk>/logout", DeviceLogoutView.as_view(), name="device-logout"),
    path("<uuid:pk>/events", DeviceEventsView.as_view(), name="device-events"),
]
