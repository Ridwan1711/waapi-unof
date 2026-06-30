from django.contrib import admin

from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "workspace", "is_active", "last_used_at", "created_at")
    list_filter = ("workspace",)
    search_fields = ("name", "prefix", "workspace__name")
    readonly_fields = ("prefix", "hashed_key", "last_used_at")
