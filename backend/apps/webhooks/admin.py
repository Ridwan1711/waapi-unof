from django.contrib import admin

from .models import Webhook, WebhookDelivery


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("url", "workspace", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("url", "workspace__name")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("event_type", "webhook", "status", "attempts", "response_status", "created_at")
    list_filter = ("status", "event_type")
    readonly_fields = ("payload", "response_body")
    date_hierarchy = "created_at"
