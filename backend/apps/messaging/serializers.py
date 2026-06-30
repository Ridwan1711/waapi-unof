from __future__ import annotations

import base64
import binascii

from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "device",
            "direction",
            "message_type",
            "address",
            "body",
            "status",
            "wa_message_id",
            "error",
            "created_at",
        ]
        read_only_fields = fields


class MediaInputSerializer(serializers.Serializer):
    mime_type = serializers.CharField()
    data_base64 = serializers.CharField()
    filename = serializers.CharField(required=False, allow_blank=True, default="")
    caption = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_data_base64(self, value: str) -> str:
        try:
            base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise serializers.ValidationError("Invalid base64 data.") from exc
        return value


class SendMessageSerializer(serializers.Serializer):
    device = serializers.UUIDField()
    to = serializers.CharField()
    type = serializers.ChoiceField(choices=["text", "media"], default="text")
    text = serializers.CharField(required=False, allow_blank=True, default="")
    media = MediaInputSerializer(required=False)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if attrs["type"] == "text" and not attrs.get("text"):
            raise serializers.ValidationError({"text": "text is required when type=text."})
        if attrs["type"] == "media" and not attrs.get("media"):
            raise serializers.ValidationError({"media": "media is required when type=media."})
        return attrs
