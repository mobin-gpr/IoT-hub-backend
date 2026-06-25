"""
OpenAPI schema definitions for Session Management endpoints.

All docstrings are in English, with user-facing messages in Persian (in examples).
"""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from ..serializers import UserSessionSerializer

# ============================================================================
# 📱 Session Management Endpoints
# ============================================================================

user_session_list_schema = extend_schema(
    tags=["📱 Session Management"],
    summary="📋 List User Sessions",
    description="""
    Retrieve a list of all sessions for the authenticated user.

    **GET /api/v1/accounts/sessions/**

    This endpoint returns all active and inactive sessions with detailed device information,
    IP address, and activity status.

    ## 📋 Response Includes:
    - **Session Info:** ID, device name, device type, browser, OS
    - **Network Info:** IP address, location (if available)
    - **Status:** Active/Inactive status
    - **Timestamps:** Creation date and last activity
    - **Metadata:** Indicates if session is older than 7 days (`is_old_session`)
    - **Permission:** Indicates if the session can revoke others (`can_revoke_others`)

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)

    ## 📊 Success Response (200 OK)
    Returns a list of `UserSessionSerializer` objects.

    ## ⚠️ Error Responses:
    - **401:** Unauthorized - Invalid or missing JWT token
    - **500:** Internal server error
    """,
    responses={
        200: OpenApiResponse(
            response=UserSessionSerializer(many=True),
            description="✅ List of user sessions retrieved successfully",
            examples=[
                OpenApiExample(
                    name="Success Response Example",
                    value=[
                        {
                            "id": 1,
                            "device_name": "Chrome on Windows",
                            "device_type": "desktop",
                            "browser": "Chrome",
                            "os": "Windows 10",
                            "ip_address": "192.168.1.1",
                            "location": "Tehran, IR",
                            "is_active": True,
                            "last_activity": "2026-06-25T20:30:00Z",
                            "created_at": "2026-06-25T19:00:00Z",
                            "is_old_session": False,
                            "can_revoke_others": False,
                        },
                        {
                            "id": 2,
                            "device_name": "Safari on iPhone",
                            "device_type": "mobile",
                            "browser": "Safari",
                            "os": "iOS 17",
                            "ip_address": "10.0.0.5",
                            "location": "Mashhad, IR",
                            "is_active": True,
                            "last_activity": "2026-06-25T15:00:00Z",
                            "created_at": "2026-06-20T10:00:00Z",
                            "is_old_session": True,
                            "can_revoke_others": True,
                        },
                    ],
                ),
            ],
        ),
        401: OpenApiResponse(
            description="🔒 Unauthorized - Authentication required",
            examples=[
                OpenApiExample(
                    name="Unauthorized Response",
                    value={"detail": "اعتبارسنجی نشده است."},
                ),
            ],
        ),
    },
)


revoke_session_schema = extend_schema(
    tags=["📱 Session Management"],
    summary="🚫 Revoke a Specific Session",
    description="""
    Revoke (deactivate) a specific user session by its ID.

    **DELETE /api/v1/accounts/sessions/{session_id}/**

    If the session being revoked is older than 7 days, all other active sessions
    will also be revoked automatically (security measure).

    ## 📋 Request Parameters (Path):
    - `session_id` (required): ID of the session to revoke

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - Only the owner of the session can revoke it

    ## 📊 Success Response (200 OK):
    - Returns a confirmation message

    ## ⚠️ Error Responses:
    - **401:** Unauthorized - Invalid or missing JWT token
    - **404:** Session not found or does not belong to the user
    - **500:** Internal server error
    """,
    parameters=[
        OpenApiParameter(
            name="session_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
            description="🆔 ID of the session to revoke",
            examples=[
                OpenApiExample("Example Session ID", value=1),
            ],
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="✅ Session revoked successfully",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={"detail": "جلسه با موفقیت لغو شد."},
                ),
            ],
        ),
        401: OpenApiResponse(
            description="🔒 Unauthorized - Authentication required",
            examples=[
                OpenApiExample(
                    name="Unauthorized Response",
                    value={"detail": "اعتبارسنجی نشده است."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="❌ Not Found - Session not found",
            examples=[
                OpenApiExample(
                    name="Not Found Response",
                    value={"detail": "جلسه مورد نظر یافت نشد."},
                ),
            ],
        ),
    },
)


revoke_all_sessions_schema = extend_schema(
    tags=["📱 Session Management"],
    summary="🚫 Revoke All Sessions Except Current",
    description="""
    Revoke (deactivate) all active sessions for the authenticated user,
    except the current session.

    **POST /api/v1/accounts/sessions/revoke-all/**

    This endpoint is useful for logging out from all other devices while keeping
    the current device active. The current session is identified by matching
    the `User-Agent` and IP address.

    ## 📋 Process Flow:
    1. 🔍 Identifies the current session using `User-Agent` and IP address
    2. 🗑️ Revokes all other active sessions (sets `is_active=False`)
    3. 📤 Returns the count of revoked sessions

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)

    ## 📊 Success Response (200 OK):
    - Returns confirmation message with the number of revoked sessions

    ## ⚠️ Error Responses:
    - **401:** Unauthorized - Invalid or missing JWT token
    - **500:** Internal server error
    """,
    responses={
        200: OpenApiResponse(
            description="✅ All other sessions revoked successfully",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={
                        "detail": "2 جلسه دیگر با موفقیت لغو شدند.",
                        "revoked_count": 2,
                    },
                ),
                OpenApiExample(
                    name="No Other Sessions",
                    value={
                        "detail": "0 جلسه دیگر با موفقیت لغو شدند.",
                        "revoked_count": 0,
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="🔒 Unauthorized - Authentication required",
            examples=[
                OpenApiExample(
                    name="Unauthorized Response",
                    value={"detail": "اعتبارسنجی نشده است."},
                ),
            ],
        ),
    },
)
