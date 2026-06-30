from __future__ import annotations

from rest_framework import serializers

from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "phone_number", "status", "provider", "last_seen_at", "created_at"]
        read_only_fields = fields


class DeviceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    provider = serializers.ChoiceField(
        choices=Device.Provider.choices, default=Device.Provider.WWEBJS
    )
