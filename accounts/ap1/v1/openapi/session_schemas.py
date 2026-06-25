"""OpenAPI schemas for session management endpoints."""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

# Session List Schema
user_session_list_schema = extend_schema(
    summary="📋 لیست جلسات کاربر",
    description="""
    لیست تمام جلسات کاربر احراز هویت شده را برمی‌گرداند.

    **GET /api/v1/accounts/sessions/**

    این اندپوینت تمام جلسات فعال و غیرفعال کاربر را نشان می‌دهد
    شامل اطلاعات کامل دستگاه، IP آدرس، و وضعیت فعالیت.

    **پاسخ:**
    - لیست جلسات با اطلاعات دستگاه
    - وضعیت فعال/غیرفعال هر جلسه
    - تاریخ ایجاد و آخرین فعالیت
    - نشان‌دهنده جلسات قدیمی (بیش از ۷ روز)
    """,
    tags=["📱 مدیریت جلسات"],
    responses={
        200: OpenApiResponse(
            description="لیست جلسات با موفقیت دریافت شد",
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            description="احراز هویت ناموفق - توکن نامعتبر یا منقضی شده",
        ),
    },
)


# Revoke Session Schema
revoke_session_schema = extend_schema(
    summary="🚫 لغو یک جلسه خاص",
    description="""
    یک جلسه خاص را لغو (غیرفعال) می‌کند.

    **DELETE /api/v1/accounts/sessions/{session_id}/**

    اگر جلسه‌ای که لغو می‌شود قدیمی‌تر از ۷ روز باشد،
    تمام جلسات دیگر فعال نیز لغو خواهند شد.

    **پارامترها:**
    - `session_id`: شناسه جلسه (در URL)

    **پاسخ:**
    - پیام موفقیت‌آمیز بودن لغو جلسه
    - اگر جلسه قدیمی باشد، تعداد کل جلسات لغو شده
    """,
    tags=["📱 مدیریت جلسات"],
    parameters=[
        OpenApiParameter(
            name="session_id",
            type=OpenApiTypes.INT,
            location="path",
            description="شناسه جلسه برای لغو",
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="جلسه با موفقیت لغو شد",
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            description="احراز هویت ناموفق - توکن نامعتبر یا منقضی شده",
        ),
        404: OpenApiResponse(
            description="جلسه مورد نظر یافت نشد",
        ),
    },
)


# Revoke All Sessions Schema
revoke_all_sessions_schema = extend_schema(
    summary="🚫 لغو تمام جلسات به جز جلسه فعلی",
    description="""
    تمام جلسات فعال کاربر را به جز جلسه فعلی لغو می‌کند.

    **POST /api/v1/accounts/sessions/revoke-all/**

    این اندپوینت برای خروج از تمام دستگاه‌ها به جز دستگاه فعلی مفید است.
    جلسه فعلی بر اساس User Agent و IP آدرس تشخیص داده می‌شود.

    **پاسخ:**
    - پیام موفقیت‌آمیز بودن لغو جلسات
    - تعداد جلسات لغو شده
    """,
    tags=["📱 مدیریت جلسات"],
    responses={
        200: OpenApiResponse(
            description="تمام جلسات دیگر با موفقیت لغو شدند",
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            description="احراز هویت ناموفق - توکن نامعتبر یا منقضی شده",
        ),
    },
)
