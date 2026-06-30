from __future__ import annotations

from rest_framework import serializers

from .models import AutoReplyRule


class AutoReplyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoReplyRule
        fields = [
            "id",
            "device",
            "name",
            "match_type",
            "pattern",
            "case_sensitive",
            "response_body",
            "is_active",
            "priority",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
