from django.urls import path
from .views import (
    DeviceCreateView,
    DeviceAuthView,
    DeviceUpdateDeleteView,
    CacheAllACLsView,
)

app_name = "devices_api_v1"

urlpatterns = [
    path("create", DeviceCreateView.as_view(), name="device_create"),
    path("auth/", DeviceAuthView.as_view(), name="device_auth"),
    path("<uuid:uuid>/", DeviceUpdateDeleteView.as_view(), name="device_update_delete"),
    path("cache-acls/", CacheAllACLsView.as_view(), name="cache_all_acls"),
]
