from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره تلفن الزامی است")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_approved", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("کاربر ادمین باید is_staff=True داشته باشد")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("کاربر ادمین باید is_superuser=True داشته باشد")

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
    )
    full_name = models.CharField(max_length=255, blank=True)
    is_approved = models.BooleanField(
        default=False, help_text="نشان می‌دهد که کاربر تایید شده است"
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class UserSession(models.Model):
    """Model to track user login sessions with device information."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sessions", verbose_name="کاربر"
    )
    device_name = models.CharField(
        max_length=255, blank=True, verbose_name="نام دستگاه"
    )
    device_type = models.CharField(
        max_length=50, blank=True, verbose_name="نوع دستگاه"
    )  # e.g., 'mobile', 'desktop', 'tablet'
    browser = models.CharField(max_length=255, blank=True, verbose_name="مرورگر")
    os = models.CharField(max_length=255, blank=True, verbose_name="سیستم عامل")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP آدرس"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    location = models.CharField(max_length=255, blank=True, verbose_name="موقعیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="آخرین فعالیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "جلسه کاربر"
        verbose_name_plural = "جلسات کاربران"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone_number} - {self.device_name or 'Unknown Device'}"

    def revoke(self):
        """Revoke this session by marking it as inactive."""
        self.is_active = False
        self.save()

    @property
    def is_old_session(self):
        """Check if session is older than 7 days."""
        return (timezone.now() - self.created_at).days > 7
