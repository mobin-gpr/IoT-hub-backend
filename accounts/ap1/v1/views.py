import secrets
import time
import logging

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView
from rest_framework.generics import ListAPIView, DestroyAPIView

from utils.sms import send_verification_code
from utils.device_info import get_device_info, get_client_ip
from accounts.models import UserSession
from .serializers import (
    LoginSendOTPSerializer,
    OTPVerifySerializer,
    UserSessionSerializer,
)
from .openapi.authentication_schemas import (
    login_send_otp_schema,
    login_verify_otp_schema,
    token_refresh_schema,
)
from .openapi.session_schemas import (
    user_session_list_schema,
    revoke_session_schema,
    revoke_all_sessions_schema,
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

                # Track user session
                user_agent = request.META.get("HTTP_USER_AGENT", "")
                ip_address = get_client_ip(request)
                device_info = get_device_info(user_agent)

                UserSession.objects.create(
                    user=user,
                    device_name=device_info["device_name"],
                    device_type=device_info["device_type"],
                    browser=device_info["browser"],
                    os=device_info["os"],
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                # Prepare user info
                user_info = {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_image": None,
                    "role": "regular_user",
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


@token_refresh_schema
class CustomTokenRefreshView(SimpleJWTTokenRefreshView):
    """
    🔄 Refresh JWT access token using refresh token.

    POST /api/v1/accounts/token/refresh/

    Returns a new access token.
    """

    pass


# ============================================================================
# 📱 Session Management Views
# ============================================================================


@user_session_list_schema
class UserSessionListView(ListAPIView):
    """
    📋 List all user sessions with device information.

    GET /api/v1/accounts/sessions/

    Returns a list of all sessions for the authenticated user,
    including device details, IP address, and activity status.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSessionSerializer

    def get_queryset(self):
        """
        Return sessions for the authenticated user.
        """
        user = self.request.user
        queryset = user.sessions.all()

        # Add can_revoke_others field to each session
        for session in queryset:
            session.can_revoke_others = session.is_old_session

        return queryset


@revoke_session_schema
class RevokeSessionView(DestroyAPIView):
    """
    🚫 Revoke a specific user session.

    DELETE /api/v1/accounts/sessions/{id}/

    Revokes (deactivates) a specific session. If the session being revoked
    is older than 7 days, all other active sessions will also be revoked.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSessionSerializer
    lookup_url_kwarg = "session_id"

    def get_queryset(self):
        """
        Return sessions for the authenticated user only.
        """
        return self.request.user.sessions.all()

    def destroy(self, request, *args, **kwargs):
        """
        Revoke the specific session only.
        """
        try:
            session = self.get_object()

            # Revoke the requested session only
            session.revoke()

            return Response(
                {"detail": "جلسه با موفقیت لغو شد."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            accounts_logger.error(
                f"Error in RevokeSessionView for user {request.user.id}: {e}",
                exc_info=True,
            )
            return Response(
                {"detail": "خطای داخلی سرور."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@revoke_all_sessions_schema
class RevokeAllSessionsView(APIView):
    """
    🚫 Revoke all active sessions except the current one.

    POST /api/v1/accounts/sessions/revoke-all/

    Revokes all active sessions for the authenticated user except
    the current session. Useful for logging out from all other devices.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Revoke all sessions except the current one.
        """
        try:
            # Get current session based on user agent and IP
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            ip_address = get_client_ip(request)

            # Find current session (most recent with matching user agent and IP)
            current_session = (
                request.user.sessions.filter(
                    user_agent=user_agent, ip_address=ip_address, is_active=True
                )
                .order_by("-created_at")
                .first()
            )

            # Revoke all other active sessions
            other_sessions = request.user.sessions.filter(is_active=True)
            if current_session:
                other_sessions = other_sessions.exclude(id=current_session.id)

            revoked_count = other_sessions.count()
            other_sessions.update(is_active=False)

            return Response(
                {
                    "detail": f"{revoked_count} جلسه دیگر با موفقیت لغو شدند.",
                    "revoked_count": revoked_count,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            accounts_logger.error(
                f"Error in RevokeAllSessionsView for user {request.user.id}: {e}",
                exc_info=True,
            )
            return Response(
                {"detail": "خطای داخلی سرور."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
