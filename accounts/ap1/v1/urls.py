from django.urls import path
from .views import (
    LoginSendOTPView,
    LoginVerifyOTPView,
    CustomTokenRefreshView,
    UserSessionListView,
    RevokeSessionView,
    RevokeAllSessionsView,
)

app_name = "accounts_api_v1"

urlpatterns = [
    path("login/", LoginSendOTPView.as_view(), name="login_send_otp"),
    path("login/verify/", LoginVerifyOTPView.as_view(), name="login_verify_otp"),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "sessions/",
        UserSessionListView.as_view(),
        name="user_sessions_list",
    ),
    path(
        "sessions/<int:session_id>/",
        RevokeSessionView.as_view(),
        name="revoke_session",
    ),
    path(
        "sessions/revoke-all/",
        RevokeAllSessionsView.as_view(),
        name="revoke_all_sessions",
    ),
]
