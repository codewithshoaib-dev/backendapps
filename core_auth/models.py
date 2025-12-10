from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group, Permission

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="custom_roles")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]



class User(AbstractUser):
    """
    Production-ready User model for SaaS applications.

    """

    # Use email as unique identifier for login
    email = models.EmailField("email address", unique=True, db_index=True)

    # Optional SaaS-related fields
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, db_index=True)
    last_login = models.DateTimeField(blank=True, null=True, db_index=True)
    
    # Profile / SaaS usage
    company_name = models.CharField(max_length=255, blank=True, null=True)
    timezone = models.CharField(max_length=64, default="UTC")
    avatar_url = models.URLField(blank=True, null=True)
    
    # Phone field with validation (optional for multi-factor auth)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, db_index=True)

    # SaaS plan / subscription
    plan = models.CharField(max_length=32, default="free", db_index=True)

    roles = models.ManyToManyField(Role, blank=True, related_name="users")

    USERNAME_FIELD = "email"  # or set 'username' if you want username login only

    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()

    def has_role(self, role_name: str) -> bool:
        return self.roles.filter(name=role_name).exists()

    def has_any_role(self, *role_names) -> bool:
        return self.roles.filter(name__in=role_names).exists()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["date_joined"]),
            models.Index(fields=["plan"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"


