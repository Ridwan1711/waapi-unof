from __future__ import annotations

from rest_framework import serializers

from .models import Webhook, WebhookDelivery


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ["id", "url", "events", "secret", "description", "is_active", "created_at"]
        read_only_fields = ["id", "secret", "created_at"]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "event_type",
            "status",
            "attempts",
            "response_status",
            "next_retry_at",
            "delivered_at",
            "created_at",
        ]
        read_only_fields = fields
