from django.urls import path
from .views import DeviceCreateView, DeviceAuthView

app_name = "devices_api_v1"

urlpatterns = [
    path("create", DeviceCreateView.as_view(), name="device_create"),
    path("auth/", DeviceAuthView.as_view(), name="device_auth"),
]
