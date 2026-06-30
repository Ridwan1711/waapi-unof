from django.contrib import admin

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "status", "provider", "phone_number", "last_seen_at")
    list_filter = ("status", "provider")
    search_fields = ("name", "phone_number", "workspace__name")
    readonly_fields = ("worker_id", "session_ref", "last_seen_at")
