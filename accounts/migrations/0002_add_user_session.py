# Generated migration for UserSession model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "device_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="نام دستگاه"
                    ),
                ),
                (
                    "device_type",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="نوع دستگاه"
                    ),
                ),
                (
                    "browser",
                    models.CharField(blank=True, max_length=255, verbose_name="مرورگر"),
                ),
                (
                    "os",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="سیستم عامل"
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        null=True, blank=True, verbose_name="IP آدرس"
                    ),
                ),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                (
                    "location",
                    models.CharField(blank=True, max_length=255, verbose_name="موقعیت"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                (
                    "last_activity",
                    models.DateTimeField(auto_now=True, verbose_name="آخرین فعالیت"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="sessions",
                        to="accounts.user",
                        verbose_name="کاربر",
                    ),
                ),
            ],
            options={
                "verbose_name": "جلسه کاربر",
                "verbose_name_plural": "جلسات کاربران",
                "ordering": ["-created_at"],
            },
        ),
    ]
