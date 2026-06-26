"""
OpenAPI schema definitions for Device endpoints.
All docstrings in English, user-facing messages in Persian in examples.
"""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from ..serializers import DeviceCreateSerializer, DeviceAuthSerializer

device_create_schema = extend_schema(
    tags=["📱 Devices"],
    summary="📲 Create a New IoT Device",
    description="""
    Create a new IoT device with auto-generated secure password.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser or belong to the 'device_creators' group

    ## 📋 Process Flow:
    1. ✅ Validates input data (name, username, model)
    2. 🔑 Auto-generates a strong password (16 chars, mix of upper/lower/digits/special)
    3. 🔒 Hashes the password before storing in database
    4. 📤 Returns the device details with `plain_password` (visible only once)

    ## 📝 Request Body:
    - `name` (required): Human-readable device name
    - `model` (optional): Device model (e.g., ESP32, Raspberry Pi)
    - `username` (required): Unique username for device authentication

    ## 📊 Response:
    - Returns the created device details including `plain_password`
    - `uuid`, `owner`, `created_at`, `updated_at` are set automatically
    - ⚠️ The `plain_password` is shown only in this response
      and will never be accessible again

    ## ⚠️ Error Responses:
    - **400**: Invalid data (duplicate username, empty name, etc.)
    - **401**: Unauthorized (missing/invalid JWT)
    - **403**: Forbidden (insufficient permissions)
    """,
    request=DeviceCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="✅ Device created successfully with plain password",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={
                        "detail": "دستگاه با موفقیت ایجاد شد.",
                        "device": {
                            "uuid": "550e8400-e29b-41d4-a716-446655440000",
                            "name": "Sensor_01",
                            "model": "ESP32",
                            "username": "sensor_01",
                            "plain_password": "aB3#xY9$mN2@kL7!",
                            "is_active": True,
                            "owner": 1,
                            "created_at": "2026-06-26T10:00:00Z",
                            "updated_at": "2026-06-26T10:00:00Z",
                        },
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="❌ Bad Request - Validation error",
            examples=[
                OpenApiExample(
                    name="Duplicate Username",
                    value={
                        "username": [
                            "این نام کاربری قبلاً برای دستگاه دیگری ثبت شده است."
                        ]
                    },
                ),
                OpenApiExample(
                    name="Empty Name",
                    value={"name": ["نام دستگاه نمی‌تواند خالی باشد."]},
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
        403: OpenApiResponse(
            description="🚫 Forbidden - Insufficient permissions",
            examples=[
                OpenApiExample(
                    name="Forbidden Response",
                    value={"detail": "شما مجوز ایجاد دستگاه را ندارید."},
                ),
            ],
        ),
    },
)


device_auth_schema = extend_schema(
    tags=["📱 Devices"],
    summary="🔐 Device Authentication for EMQX",
    description="""
    Authenticate IoT devices connecting via EMQX MQTT broker.

    ## 📋 Process Flow:
    1. 📥 Receives username and password from EMQX
    2. 🔍 Checks if username exists in Device model
    3. ✅ Verifies the password (hashed comparison)
    4. 🚦 Checks if the device is active
    5. 📤 Returns `allow` or `deny` result

    ## 🔐 Authentication:
    - No authentication required (AllowAny)
    - This endpoint is called by EMQX, not by users

    ## 📝 Request Body:
    - `username`: Device username (string, required)
    - `password`: Device password (string, required)

    ## 📊 Response:
    - `result`: "allow" or "deny"

    ## ⚠️ Important:
    - Always returns HTTP 200, even for denied requests (EMQX expects 200)
    - The response body determines allow/deny, not HTTP status code
    """,
    request=DeviceAuthSerializer,
    responses={
        200: OpenApiResponse(
            description="✅ Authentication result (always 200)",
            examples=[
                OpenApiExample(
                    name="Allow Response",
                    value={"result": "allow"},
                ),
                OpenApiExample(
                    name="Deny Response",
                    value={"result": "deny"},
                ),
            ],
        ),
    },
)
