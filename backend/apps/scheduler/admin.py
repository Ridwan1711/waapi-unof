from django.contrib import admin

from .models import ScheduledMessage


@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ("run_at", "status", "device", "workspace", "last_run_at")
    list_filter = ("status",)
    search_fields = ("workspace__name", "device__name")
    date_hierarchy = "run_at"
