from django.conf import settings
from django.core import signing
from .email_utils import send_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from django.contrib.auth import get_user_model

User = get_user_model()

email_verification_signer = signing.TimestampSigner()
password_reset_token = PasswordResetTokenGenerator()

def generate_email_verification_token(user: User) -> str:  # type: ignore[override]
    """Return a signed token that expires after a certain duration."""
    data = {"user_id": user.pk}
    return signing.dumps(data, salt="email-verify")

def verify_email_token(token: str) -> User | None:  # type: ignore[override]
    """Return user if token is valid and not expired."""
    try:
        data = signing.loads(token, salt="email-verify", max_age=60 * 60 * 24)
        return User.objects.get(pk=data["user_id"])
    except Exception:
        return None

def send_verification_email(user: User, request):  # type: ignore[override]
    """Send a verification link with signed token."""
    token = generate_email_verification_token(user)
    verify_url = request.build_absolute_uri(reverse("core_auth:verify-email")) + f"?token={token}"
    send_email(
        subject="Verify your email",
        body_text=f"Click to verify your email: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

def send_password_reset_email(user: User, request):  # type: ignore[override]
    """Send password reset link using Django's token generator."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)
    reset_url = request.build_absolute_uri(reverse("core_auth:password-reset-confirm")) + f"?uid={uid}&token={token}"
    send_email(
        subject="Password reset",
        body_text=f"Click to reset your password: {reset_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
