from django.contrib import admin

from .models import DailyUsage


@admin.register(DailyUsage)
class DailyUsageAdmin(admin.ModelAdmin):
    list_display = ("date", "workspace", "messages_sent", "messages_received", "media_sent")
    list_filter = ("date",)
    search_fields = ("workspace__name",)
    date_hierarchy = "date"
