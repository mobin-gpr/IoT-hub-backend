import secrets
import time
import logging

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from utils.sms import send_verification_code
from .serializers import (
    LoginSendOTPSerializer,
    OTPVerifySerializer,
)
from .openapi.authentication_schemas import (
    login_send_otp_schema,
    login_verify_otp_schema,
)

# --- Logging Setup ---
accounts_logger = logging.getLogger("accounts")
# --- End Logging Setup ---

# --- Constants ---
try:
    CACHE_TIMEOUT = settings.AUTH_CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 120

try:
    OTP_LENGTH = settings.AUTH_OTP_LENGTH
except AttributeError:
    OTP_LENGTH = 5

# Get custom user model
User = get_user_model()


# ============================================================================
# 🔐 Authentication Views
# ============================================================================


@login_send_otp_schema
class LoginSendOTPView(APIView):
    """
    Send OTP for login/signup. If user exists, login flow; if not, signup flow.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSendOTPSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                phone_number = serializer.validated_data["phone_number"]

                # Check for existing active OTP
                cache_key_otp = f"otp_{phone_number}"
                cached_data = cache.get(cache_key_otp)

                if cached_data:
                    expires_at = cached_data.get("expires_at")
                    now = time.time()
                    if expires_at and expires_at > now:
                        remaining_ttl = int(expires_at - now)
                        if remaining_ttl > 0:
                            message = f"یک کد فعال برای این شماره وجود دارد. لطفاً پس از {remaining_ttl} ثانیه دوباره تلاش کنید."
                            return Response(
                                {"detail": message, "ttl": remaining_ttl},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                # Generate OTP
                otp_code = "".join(
                    secrets.choice("0123456789") for _ in range(OTP_LENGTH)
                )

                # Store OTP with expiration
                current_time = time.time()
                expires_at = current_time + CACHE_TIMEOUT
                otp_data = {"code": otp_code, "expires_at": expires_at}
                cache.set(cache_key_otp, otp_data, timeout=CACHE_TIMEOUT)

                # Send OTP via SMS
                send_verification_code(phone_number, otp_code)

                return Response(
                    {"detail": "کد تایید ارسال شد."},
                    status=status.HTTP_200_OK,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            accounts_logger.error(
                f"Error in LoginSendOTPView for {request.data.get('phone_number')}: {e}",
                exc_info=True,
            )
            return Response(
                {"detail": "خطای داخلی سرور."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@login_verify_otp_schema
class LoginVerifyOTPView(APIView):
    """
    Verify OTP and return JWT tokens. Creates user if not exists.
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                phone_number = serializer.validated_data["phone_number"]
                otp_code = serializer.validated_data["otp_code"]

                cache_key_otp = f"otp_{phone_number}"
                cached_otp_data = cache.get(cache_key_otp)

                stored_otp_code = None
                if cached_otp_data and isinstance(cached_otp_data, dict):
                    stored_otp_code = cached_otp_data.get("code")

                if not stored_otp_code or stored_otp_code != otp_code:
                    return Response(
                        {"detail": "کد تایید نامعتبر یا منقضی شده است."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # OTP valid, delete it
                cache.delete(cache_key_otp)

                # Get or create user
                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={
                        "first_name": "",
                        "last_name": "",
                        "is_active": True,
                        "is_approved": False,
                    },
                )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                # Prepare user info
                user_info = {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_image": None,  # No profile image for new users
                    "role": "regular_user",  # Default role
                    "is_approved": user.is_approved,
                }

                response_data = {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": user_info,
                }

                accounts_logger.info(
                    f"User {user.id} authenticated via OTP. Created: {created}"
                )

                return Response(response_data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            accounts_logger.error(
                f"Error in LoginVerifyOTPView for {request.data.get('phone_number')}: {e}",
                exc_info=True,
            )
            return Response(
                {"detail": "خطای داخلی سرور."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
