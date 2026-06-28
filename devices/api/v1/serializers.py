from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
import secrets
import string

from devices.models import Device
from devices.redis_acl import cache_device_acl


class DeviceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new device.
    Password is auto-generated and returned only once as plain_password.
    """

    plain_password = serializers.CharField(
        read_only=True, help_text="Auto-generated plain password (shown only once)"
    )

    class Meta:
        model = Device
        fields = [
            "uuid",
            "name",
            "model",
            "username",
            "plain_password",
            "is_active",
            "topics",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "owner", "created_at", "updated_at"]

    def generate_secure_password(self):
        """Generate a strong random password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(16))
        return password

    def create(self, validated_data):
        """
        Create a new device with auto-generated secure password.
        Cache device ACL in Redis after creation.
        """
        # Generate secure password
        plain_password = self.generate_secure_password()
        hashed_password = make_password(plain_password)

        # Set password and owner
        validated_data["password"] = hashed_password

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["owner"] = request.user

        device = super().create(validated_data)

        # Cache device ACL in Redis
        cache_device_acl(device)

        # Attach plain_password to the instance for serialization
        device.plain_password = plain_password

        return device

    def validate_username(self, value):
        """
        Ensure username is unique.
        """
        if Device.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "این نام کاربری قبلاً برای دستگاه دیگری ثبت شده است."
            )
        return value

    def validate_name(self, value):
        """
        Ensure name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("نام دستگاه نمی‌تواند خالی باشد.")
        return value.strip()


class DeviceAuthSerializer(serializers.Serializer):
    """
    Serializer for EMQX device authentication.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        """
        Validate device credentials.
        """
        username = data.get("username")
        password = data.get("password")

        try:
            device = Device.objects.get(username=username)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Check if device is active
        if not device.is_active:
            raise serializers.ValidationError("Device is inactive")

        # Verify password
        if not check_password(password, device.password):
            raise serializers.ValidationError("Invalid credentials")

        # Attach device to validated data for later use
        data["device"] = device
        return data


class DeviceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a device.
    """

    class Meta:
        model = Device
        fields = [
            "name",
            "model",
            "is_active",
            "topics",
        ]

    def update(self, instance, validated_data):
        """
        Update device and cache ACL in Redis.
        """
        device = super().update(instance, validated_data)

        # Cache updated device ACL in Redis
        cache_device_acl(device)

        return device
