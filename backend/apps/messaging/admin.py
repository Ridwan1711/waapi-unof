from django.contrib import admin

from .models import MediaAsset, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "direction", "message_type", "status", "address", "device")
    list_filter = ("direction", "message_type", "status")
    search_fields = ("address", "wa_message_id", "body")
    readonly_fields = ("wa_message_id",)
    date_hierarchy = "created_at"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "mime_type", "size", "workspace", "created_at")
    search_fields = ("original_filename", "checksum")
