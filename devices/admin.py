from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "uuid", "username", "owner", "is_active", "created_at")
    list_filter = ("is_active", "owner", "created_at")
    search_fields = ("name", "uuid", "username", "model")
    readonly_fields = ("uuid", "created_at", "updated_at")