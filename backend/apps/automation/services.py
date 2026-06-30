"""Auto-reply matching + dispatch."""

from __future__ import annotations

import logging
import re

from django.db.models import Q

from .models import AutoReplyRule

logger = logging.getLogger(__name__)


def _matches(rule: AutoReplyRule, text: str) -> bool:
    if rule.match_type == AutoReplyRule.Match.REGEX:
        flags = 0 if rule.case_sensitive else re.IGNORECASE
        try:
            return re.search(rule.pattern, text, flags) is not None
        except re.error:
            logger.warning("invalid regex in auto-reply rule %s", rule.id)
            return False

    haystack = text if rule.case_sensitive else text.lower()
    needle = rule.pattern if rule.case_sensitive else rule.pattern.lower()
    if rule.match_type == AutoReplyRule.Match.EXACT:
        return haystack == needle
    if rule.match_type == AutoReplyRule.Match.CONTAINS:
        return needle in haystack
    if rule.match_type == AutoReplyRule.Match.STARTS_WITH:
        return haystack.startswith(needle)
    return False


def handle_inbound_auto_reply(device, from_address: str, body: str) -> AutoReplyRule | None:
    """Evaluate active rules (device-specific or workspace-wide) by priority and
    send the first matching reply. Returns the rule that fired, if any."""
    if not body or not from_address:
        return None

    rules = (
        AutoReplyRule.objects.filter(workspace=device.workspace, is_active=True)
        .filter(Q(device=device) | Q(device__isnull=True))
        .order_by("-priority", "created_at")
    )
    for rule in rules:
        if _matches(rule, body):
            # Imported lazily to avoid a circular import with the messaging app.
            from apps.messaging.services import send_message

            send_message(
                device=device, to=from_address, message_type="text", text=rule.response_body
            )
            return rule
    return None
