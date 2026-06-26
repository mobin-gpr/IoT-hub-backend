from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from devices.permissions import CanCreateDevice
from .serializers import DeviceCreateSerializer, DeviceAuthSerializer
from .openapi.device_schemas import device_create_schema, device_auth_schema


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
