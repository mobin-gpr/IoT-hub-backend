from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
import re

User = get_user_model()

# OTP length from settings
OTP_LENGTH = getattr(settings, "AUTH_OTP_LENGTH", 5)


class BasePhoneSerializer(serializers.Serializer):
    """
    Base serializer with phone number validation for Iranian mobile numbers.
    """

    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        required=True,
        error_messages={
            "required": "وارد کردن شماره تلفن الزامی است.",
            "blank": "شماره تلفن نمی‌تواند خالی باشد.",
            "min_length": "شماره تلفن باید دقیقاً ۱۱ رقم باشد.",
            "max_length": "شماره تلفن باید دقیقاً ۱۱ رقم باشد.",
        },
    )

    def validate_phone_number(self, value):
        """
        Validate phone number format using regex from settings.
        Default pattern: r"^(09)\d{9}$"
        """
        pattern = getattr(settings, "AUTH_PHONE_REGEX_PATTERN", r"^(09)\d{9}$")
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد."
            )
        return value


class LoginSendOTPSerializer(BasePhoneSerializer):
    """
    Serializer for sending OTP for login/signup.
    """

    pass


class OTPVerifySerializer(BasePhoneSerializer):
    """
    Serializer for verifying OTP and authenticating user.
    """

    otp_code = serializers.CharField(
        max_length=OTP_LENGTH,
        min_length=OTP_LENGTH,
        required=True,
        error_messages={
            "required": "وارد کردن کد تایید الزامی است.",
            "blank": "کد تایید نمی‌تواند خالی باشد.",
            "min_length": f"کد تایید باید دقیقاً {OTP_LENGTH} رقم باشد.",
            "max_length": f"کد تایید باید دقیقاً {OTP_LENGTH} رقم باشد.",
        },
    )

    def validate_otp_code(self, value):
        """
        Ensure OTP code contains only digits.
        """
        if not value.isdigit():
            raise serializers.ValidationError("کد تایید باید فقط شامل ارقام باشد.")
        return value
