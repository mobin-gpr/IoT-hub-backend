from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from drf_spectacular.utils import extend_schema

from devices.permissions import CanCreateDevice
from .serializers import (
    DeviceCreateSerializer,
    DeviceAuthSerializer,
    DeviceUpdateSerializer,
)
from .openapi.device_schemas import (
    device_create_schema,
    device_auth_schema,
    device_retrieve_schema,
    device_update_schema,
    device_delete_schema,
    cache_all_acls_schema,
)
from devices.models import Device
from devices.redis_acl import delete_device_acl, cache_all_device_acls


class DeviceCreateView(APIView):
    """
    Create a new IoT device.
    Only superusers and users in the 'device_creators' group can create devices.
    """

    permission_classes = [IsAuthenticated, CanCreateDevice]

    @device_create_schema
    def post(self, request):
        serializer = DeviceCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            device = serializer.save()
            return Response(
                {
                    "detail": "دستگاه با موفقیت ایجاد شد.",
                    "device": DeviceCreateSerializer(device).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceAuthView(APIView):
    """
    Device authentication endpoint for EMQX.
    This endpoint receives username and password from EMQX and returns allow/deny.
    No authentication required (AllowAny) because devices are not authenticated yet.
    """

    permission_classes = [AllowAny]

    @device_auth_schema
    def post(self, request):
        serializer = DeviceAuthSerializer(data=request.data)
        if serializer.is_valid():
            # Authentication successful
            return Response({"result": "allow"}, status=status.HTTP_200_OK)

        # Authentication failed
        return Response({"result": "deny"}, status=status.HTTP_200_OK)


class DeviceUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a device.
    Only superusers and users in the 'device_creators' group can manage devices.

    GET: Retrieve device details
    PUT/PATCH: Update device details
    DELETE: Delete device
    """

    permission_classes = [IsAuthenticated, CanCreateDevice]
    queryset = Device.objects.all()
    lookup_field = "uuid"

    @device_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @device_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @device_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @device_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.request.method in ["PUT", "PATCH"]:
            return DeviceUpdateSerializer
        return DeviceCreateSerializer

    def perform_destroy(self, instance):
        """
        Delete device and its ACL from Redis.
        """
        # Delete ACL from Redis
        delete_device_acl(instance.username)
        # Delete device from database
        instance.delete()


class CacheAllACLsView(APIView):
    """
    Cache all device ACLs from PostgreSQL to Redis.
    Only superusers can access this endpoint.
    This is useful when Redis data is lost due to power outage or other issues.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    @cache_all_acls_schema
    def post(self, request):
        """
        Cache all device ACLs in Redis.
        """
        try:
            count = cache_all_device_acls()
            return Response(
                {
                    "detail": f"با موفقیت {count} دستگاه ACL کش شد.",
                    "cached_count": count,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": f"خطا در کش کردن ACLها: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
