from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core_auth.mixins import CSRFExemptMixin

from django.contrib.auth import get_user_model
from core_auth.utils import verify_email_token, send_verification_email, send_password_reset_email

User = get_user_model()

password_reset_token = PasswordResetTokenGenerator()
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class SendVerificationEmailView( APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_email_verified:
            return Response({"detail": "Email already verified"})
        send_verification_email(user, request)
        return Response({"detail": "Verification email sent"})


class VerifyEmailView(CSRFExemptMixin, APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        user = verify_email_token(token)
        if not user:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return Response({"detail": "Email verified"})


class RequestPasswordResetView(CSRFExemptMixin, APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user, request)
        except User.DoesNotExist:
            pass  # Silently ignore to prevent user enumeration
        return Response({"detail": "If that email exists, password reset link has been sent."})


class PasswordResetConfirmView(CSRFExemptMixin, APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response({"detail": "Invalid UID"}, status=status.HTTP_400_BAD_REQUEST)

        if not password_reset_token.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password has been reset."})
