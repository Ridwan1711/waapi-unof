from django.contrib import admin

from .models import AutoReplyRule


@admin.register(AutoReplyRule)
class AutoReplyRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "device", "match_type", "priority", "is_active")
    list_filter = ("match_type", "is_active")
    search_fields = ("name", "pattern", "workspace__name")
