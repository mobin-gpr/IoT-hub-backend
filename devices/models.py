from django.conf import settings
from django.db import models
import uuid


class Device(models.Model):
    """
    Model representing an IoT device.
    """

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
        help_text="Unique device identifier",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Device Name",
        help_text="Human-readable device name",
    )
    model = models.CharField(
        max_length=255,
        verbose_name="Model",
        help_text="Device model (e.g., ESP32, Raspberry Pi)",
        blank=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Username",
        help_text="Device username for authentication",
    )
    password = models.CharField(
        max_length=128,
        verbose_name="Password",
        help_text="Device password (hashed)",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="Owner",
        help_text="User who owns this device",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether the device is active and allowed to connect",
    )
    topics = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Topics",
        help_text="List of topics the device can publish/subscribe to",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.uuid})"
