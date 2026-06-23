from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
