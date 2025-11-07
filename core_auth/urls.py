from django.urls import path
from .views.auth import RegisterView, LoginView, LogoutView, get_csrf_token

from .views.password import (
    SendVerificationEmailView,
    VerifyEmailView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
)


app_name = "core_auth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("crsf/", get_csrf_token, name="crsf"),

    path("email/send/", SendVerificationEmailView.as_view(), name="send-verification"),
    path("email/verify/", VerifyEmailView.as_view(), name="verify-email"),
    path("password/reset/", RequestPasswordResetView.as_view(), name="password-reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
