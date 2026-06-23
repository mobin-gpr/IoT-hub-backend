from django.urls import path
from .views import (
    LoginSendOTPView,
    LoginVerifyOTPView,
)

app_name = "accounts_api_v1"

urlpatterns = [
    path("login/", LoginSendOTPView.as_view(), name="login_send_otp"),
    path("login/verify/", LoginVerifyOTPView.as_view(), name="login_verify_otp"),
]
