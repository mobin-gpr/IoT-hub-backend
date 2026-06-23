"""
OpenAPI schema definitions for Authentication endpoints.
All docstrings in English, user-facing messages in Persian in examples.
"""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

# Import serializers for request/response schemas
from ..serializers import LoginSendOTPSerializer, OTPVerifySerializer

# ============================================================================
# 🔐 Authentication Endpoints
# ============================================================================

login_send_otp_schema = extend_schema(
    tags=["🔐 Authentication"],
    summary="📲 Send OTP for Login/Signup",
    description="""
    Send a one-time password (OTP) to the provided phone number.

    ## 📋 Process Flow:
    1. ✅ Validates phone number format (must start with 09 and be 11 digits)
    2. 🔍 Checks if user exists: 
       - If exists → sends OTP for login
       - If not exists → sends OTP for signup (user will be created on verification)
    3. 📱 Sends OTP via SMS (or logs in development)
    4. ⏱️ Stores OTP in cache with expiration (120 seconds by default)
    5. 🚫 Prevents resend if an active OTP already exists (returns remaining TTL)

    ## 📝 Request Body:
    - `phone_number`: Iranian mobile number (required, 11 digits starting with 09)

    ## 🔐 Authentication:
    - No authentication required (AllowAny)

    ## ⚠️ Error Responses:
    - **400**: Invalid phone number format or active OTP exists
    - **500**: Server error

    ## 🎁 Success Response:
    - Returns success message and optionally remaining TTL if OTP already exists

    ## 💡 Notes:
    - OTP length is configured via `AUTH_OTP_LENGTH` (default: 5)
    - OTP timeout is configured via `AUTH_CACHE_TIMEOUT` (default: 120 seconds)
    - The same endpoint handles both login and signup (user creation happens on verification)
    """,
    request=LoginSendOTPSerializer,
    responses={
        200: OpenApiResponse(
            description="✅ OTP sent successfully",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={"detail": "کد تایید ارسال شد."},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="❌ Bad Request - Invalid phone number or active OTP exists",
            examples=[
                OpenApiExample(
                    "Invalid Phone Number",
                    value={
                        "phone_number": [
                            "شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد."
                        ]
                    },
                ),
                OpenApiExample(
                    "Active OTP Exists",
                    value={
                        "detail": "یک کد فعال برای این شماره وجود دارد. لطفاً پس از 60 ثانیه دوباره تلاش کنید.",
                        "ttl": 60,
                    },
                ),
            ],
        ),
    },
)


login_verify_otp_schema = extend_schema(
    tags=["🔐 Authentication"],
    summary="✅ Verify OTP and Authenticate",
    description="""
    Verify the OTP and authenticate the user. If user does not exist, creates a new user.

    ## 📋 Process Flow:
    1. ✅ Validates phone number and OTP
    2. 🔍 Checks OTP in cache (validates code and expiration)
    3. 👤 Retrieves or creates user (if new, creates with minimal data)
    4. 🔑 Generates JWT tokens (access + refresh)
    5. 🗑️ Deletes OTP from cache after successful verification
    6. 📤 Returns tokens and user info

    ## 📝 Request Body:
    - `phone_number`: Iranian mobile number (11 digits starting with 09)
    - `otp_code`: 5-digit OTP (length configurable)

    ## 🔐 Authentication:
    - No authentication required (AllowAny)

    ## 📊 Response Includes:
    - **access**: JWT access token (valid for 180 minutes)
    - **refresh**: JWT refresh token (valid for 7 days)
    - **user**: User object with:
      - `id`: User ID
      - `phone_number`: User phone number
      - `first_name`: User first name (empty for new users)
      - `last_name`: User last name (empty for new users)
      - `profile_image`: User profile image (null initially)
      - `role`: User role (default: 'regular_user')
      - `is_approved`: User approval status (default: False for new users)

    ## ⚠️ Error Responses:
    - **400**: Invalid OTP or expired
    - **500**: Server error

    ## 💡 Notes:
    - New users are created with `is_approved=False` (requires admin approval for corporate/organization roles later)
    - Role is set to 'personal' by default (can be extended later)
    - OTP is deleted immediately after verification to prevent reuse
    """,
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(
            description="✅ OTP verified successfully, tokens returned",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJhbGciOiJIUzI1NiIs...",
                        "refresh": "eyJhbGciOiJIUzI1NiIs...",
                        "user": {
                            "id": 1,
                            "phone_number": "09123456789",
                            "first_name": "",
                            "last_name": "",
                            "profile_image": None,
                            "role": "regular_user",
                            "is_approved": False,
                        },
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="❌ Bad Request - Invalid or expired OTP",
            examples=[
                OpenApiExample(
                    "Invalid OTP",
                    value={"detail": "کد تایید نامعتبر یا منقضی شده است."},
                ),
            ],
        ),
    },
)
