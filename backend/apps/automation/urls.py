from __future__ import annotations

from django.urls import path

from .views import AutoReplyRuleDetailView, AutoReplyRuleListCreateView

urlpatterns = [
    path("", AutoReplyRuleListCreateView.as_view(), name="autoreply-list-create"),
    path("<uuid:pk>", AutoReplyRuleDetailView.as_view(), name="autoreply-detail"),
]
