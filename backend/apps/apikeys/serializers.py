from __future__ import annotations

from rest_framework import serializers

from .models import ApiKey


class ApiKeySerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApiKey
        fields = [
            "id",
            "name",
            "prefix",
            "scopes",
            "rate_limit_per_min",
            "is_active",
            "last_used_at",
            "revoked_at",
            "created_at",
        ]
        read_only_fields = fields


class ApiKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    scopes = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    rate_limit_per_min = serializers.IntegerField(required=False, min_value=1, default=120)
