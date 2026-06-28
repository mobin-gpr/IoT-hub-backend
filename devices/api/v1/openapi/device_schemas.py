"""
OpenAPI schema definitions for Device endpoints.
All docstrings in English, user-facing messages in Persian in examples.
"""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from ..serializers import DeviceCreateSerializer, DeviceAuthSerializer, DeviceUpdateSerializer

device_create_schema = extend_schema(
    tags=["📱 Devices"],
    summary="📲 Create a New IoT Device",
    description="""
    Create a new IoT device with auto-generated secure password and topic-based ACL.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser or belong to the 'device_creators' group

    ## 📋 Process Flow:
    1. ✅ Validates input data (name, username, model, topics)
    2. 🔑 Auto-generates a strong password (16 chars, mix of upper/lower/digits/special)
    3. 🔒 Hashes the password before storing in database
    4. ⚡ Automatically caches device ACL in Redis for EMQX authorization
    5. 📤 Returns the device details with `plain_password` (visible only once)

    ## 📝 Request Body Fields:

    ### Required Fields:
    - `name` (string): Human-readable device name
      - Example: "Sensor_01", "Temperature_Monitor"
      - Cannot be empty or whitespace only

    - `username` (string): Unique username for device authentication
      - Example: "sensor_01", "device_123"
      - Must be unique across all devices
      - Used for MQTT authentication with EMQX

    ### Optional Fields:
    - `model` (string): Device model or type
      - Example: "ESP32", "Raspberry Pi", "Arduino"
      - Can be empty

    - `is_active` (boolean): Device active status
      - Default: true
      - If false, device cannot connect to EMQX

    - `topics` (array): List of topic configurations for ACL
      - Each topic is an object with:
        - `name` (string): Topic name (e.g., "status", "cmd", "config")
        - `actions` (array): List of allowed actions
          - "publish": Device can publish to this topic
          - "subscribe": Device can subscribe to this topic
      - Example:
        ```json
        [
          {"name": "status", "actions": ["publish"]},
          {"name": "cmd", "actions": ["subscribe"]},
          {"name": "config", "actions": ["publish", "subscribe"]}
        ]
        ```
      - Topic names in Redis will be formatted as: `{topic_name}_{device_uuid}`
      - If empty, device will have no MQTT permissions

    ## 📊 Response:
    - Returns the created device details including `plain_password`
    - `uuid`, `owner`, `created_at`, `updated_at` are set automatically
    - ⚠️ The `plain_password` is shown only in this response
      and will never be accessible again
    - Device ACL is automatically cached in Redis with key: `emqx:acl:{username}`

    ## 🔒 Redis ACL Format:
    After creation, the device ACL is cached in Redis as a hash:
    ```
    Key: emqx:acl:{username}
    Hash fields:
      - pub: ["status_uuid", "config_uuid"] (JSON array)
      - sub: ["cmd_uuid", "config_uuid"] (JSON array)
    ```

    ## ⚠️ Error Responses:
    - **400**: Invalid data (duplicate username, empty name, invalid topics format)
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
                            "topics": [
                                {"name": "status", "actions": ["publish"]},
                                {"name": "cmd", "actions": ["subscribe"]},
                                {"name": "config", "actions": ["publish", "subscribe"]},
                            ],
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


device_retrieve_schema = extend_schema(
    tags=["📱 Devices"],
    summary="📖 Retrieve Device Details",
    description="""
    Retrieve detailed information about a specific IoT device.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser or belong to the 'device_creators' group

    ## 📝 Parameters:
    - `uuid` (path parameter): Device UUID

    ## 📊 Response:
    - Returns complete device information including topics
    - `plain_password` is not included in retrieve response

    ## ⚠️ Error Responses:
    - **401**: Unauthorized (missing/invalid JWT)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Device not found
    """,
    responses={
        200: OpenApiResponse(
            description="✅ Device details retrieved successfully",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={
                        "uuid": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Sensor_01",
                        "model": "ESP32",
                        "username": "sensor_01",
                        "is_active": True,
                        "topics": [
                            {"name": "status", "actions": ["publish"]},
                            {"name": "cmd", "actions": ["subscribe"]},
                        ],
                        "owner": 1,
                        "created_at": "2026-06-26T10:00:00Z",
                        "updated_at": "2026-06-26T10:00:00Z",
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
        403: OpenApiResponse(
            description="🚫 Forbidden - Insufficient permissions",
            examples=[
                OpenApiExample(
                    name="Forbidden Response",
                    value={"detail": "شما مجوز مشاهده این دستگاه را ندارید."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="❌ Not Found - Device does not exist",
            examples=[
                OpenApiExample(
                    name="Not Found Response",
                    value={"detail": "دستگاه یافت نشد."},
                ),
            ],
        ),
    },
)


device_update_schema = extend_schema(
    tags=["📱 Devices"],
    summary="✏️ Update Device Information",
    description="""
    Update device information including name, model, active status, and topics.
    Device ACL in Redis is automatically updated after successful update.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser or belong to the 'device_creators' group

    ## 📝 Parameters:
    - `uuid` (path parameter): Device UUID

    ## 📋 Process Flow:
    1. ✅ Validates input data
    2. 🔄 Updates device in PostgreSQL
    3. ⚡ Automatically updates ACL in Redis
    4. 📤 Returns updated device details

    ## 📝 Request Body (partial for PATCH, full for PUT):
    - `name` (optional): Human-readable device name
    - `model` (optional): Device model
    - `is_active` (optional): Device active status
    - `topics` (optional): List of topic configurations

    ## ⚠️ Error Responses:
    - **400**: Invalid data
    - **401**: Unauthorized (missing/invalid JWT)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Device not found
    """,
    request=DeviceUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="✅ Device updated successfully",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={
                        "uuid": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Sensor_01_Updated",
                        "model": "ESP32",
                        "is_active": True,
                        "topics": [
                            {"name": "status", "actions": ["publish"]},
                            {"name": "cmd", "actions": ["subscribe"]},
                            {"name": "config", "actions": ["publish", "subscribe"]},
                        ],
                        "updated_at": "2026-06-26T11:00:00Z",
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="❌ Bad Request - Validation error",
            examples=[
                OpenApiExample(
                    name="Validation Error",
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
                    value={"detail": "شما مجوز ویرایش این دستگاه را ندارید."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="❌ Not Found - Device does not exist",
            examples=[
                OpenApiExample(
                    name="Not Found Response",
                    value={"detail": "دستگاه یافت نشد."},
                ),
            ],
        ),
    },
)


device_delete_schema = extend_schema(
    tags=["📱 Devices"],
    summary="🗑️ Delete Device",
    description="""
    Delete a device and its ACL from Redis.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser or belong to the 'device_creators' group

    ## 📝 Parameters:
    - `uuid` (path parameter): Device UUID

    ## 📋 Process Flow:
    1. 🔍 Finds device by UUID
    2. 🗑️ Deletes device ACL from Redis
    3. 🗑️ Deletes device from PostgreSQL
    4. 📤 Returns 204 No Content

    ## ⚠️ Important:
    - This action is irreversible
    - Device ACL is automatically removed from Redis
    - Device will no longer be able to connect to EMQX

    ## ⚠️ Error Responses:
    - **401**: Unauthorized (missing/invalid JWT)
    - **403**: Forbidden (insufficient permissions)
    - **404**: Device not found
    """,
    responses={
        204: OpenApiResponse(
            description="✅ Device deleted successfully (no content)",
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
                    value={"detail": "شما مجوز حذف این دستگاه را ندارید."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="❌ Not Found - Device does not exist",
            examples=[
                OpenApiExample(
                    name="Not Found Response",
                    value={"detail": "دستگاه یافت نشد."},
                ),
            ],
        ),
    },
)


cache_all_acls_schema = extend_schema(
    tags=["📱 Devices"],
    summary="⚡ Cache All Device ACLs in Redis",
    description="""
    Cache all device ACLs from PostgreSQL to Redis.
    This endpoint is useful when Redis data is lost due to power outage or other issues.

    ## 🔐 Authentication Required
    - User must be authenticated (JWT token required)
    - User must be a superuser (admin only)

    ## 📋 Process Flow:
    1. 📥 Reads all devices from PostgreSQL
    2. ⚡ Caches each device ACL in Redis
    3. 📤 Returns count of cached devices

    ## 📊 Response:
    - `detail`: Success message in Persian
    - `cached_count`: Number of devices cached

    ## ⚠️ Important:
    - This operation may take time for large numbers of devices
    - Existing ACLs in Redis will be overwritten
    - Use this when Redis data is lost or needs refresh

    ## ⚠️ Error Responses:
    - **401**: Unauthorized (missing/invalid JWT)
    - **403**: Forbidden (not a superuser)
    - **500**: Internal server error (Redis connection issue, etc.)
    """,
    responses={
        200: OpenApiResponse(
            description="✅ ACLs cached successfully",
            examples=[
                OpenApiExample(
                    name="Success Response",
                    value={
                        "detail": "با موفقیت 5 دستگاه ACL کش شد.",
                        "cached_count": 5,
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
        403: OpenApiResponse(
            description="🚫 Forbidden - Superuser only",
            examples=[
                OpenApiExample(
                    name="Forbidden Response",
                    value={"detail": "فقط ادمین می‌تواند این عملیات را انجام دهد."},
                ),
            ],
        ),
        500: OpenApiResponse(
            description="❌ Internal Server Error",
            examples=[
                OpenApiExample(
                    name="Server Error",
                    value={"detail": "خطا در کش کردن ACLها: Redis connection failed"},
                ),
            ],
        ),
    },
)
