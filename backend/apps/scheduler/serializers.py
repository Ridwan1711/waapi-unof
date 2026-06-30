from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from apps.messaging.serializers import MediaInputSerializer

from .models import ScheduledMessage


class ScheduledMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledMessage
        fields = [
            "id",
            "device",
            "run_at",
            "status",
            "payload",
            "celery_task_id",
            "last_run_at",
            "created_at",
        ]
        read_only_fields = fields


class ScheduledMessageCreateSerializer(serializers.Serializer):
    device = serializers.UUIDField()
    run_at = serializers.DateTimeField()
    to = serializers.CharField()
    type = serializers.ChoiceField(choices=["text", "media"], default="text")
    text = serializers.CharField(required=False, allow_blank=True, default="")
    media = MediaInputSerializer(required=False)

    def validate(self, attrs):
        if attrs["run_at"] <= timezone.now():
            raise serializers.ValidationError({"run_at": "run_at must be in the future."})
        if attrs["type"] == "text" and not attrs.get("text"):
            raise serializers.ValidationError({"text": "text is required when type=text."})
        if attrs["type"] == "media" and not attrs.get("media"):
            raise serializers.ValidationError({"media": "media is required when type=media."})
        return attrs
