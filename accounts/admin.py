import re
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.core.exceptions import ValidationError
from .models import User


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            return phone_number

        phone_number = str(phone_number).strip()
        phone_number = re.sub(r"[^\d]", "", phone_number)

        if phone_number.startswith("9") and len(phone_number) == 10:
            phone_number = "0" + phone_number

        if not re.match(r"^(09)\d{9}$", phone_number):
            raise ValidationError("شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد.")

        if self.instance.pk:
            existing = User.objects.filter(phone_number=phone_number).exclude(
                pk=self.instance.pk
            )
        else:
            existing = User.objects.filter(phone_number=phone_number)

        if existing.exists():
            raise ValidationError("کاربری با این شماره تلفن از قبل وجود دارد.")

        return phone_number


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="رمز عبور",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("phone_number", "full_name")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            return phone_number

        phone_number = str(phone_number).strip()
        phone_number = re.sub(r"[^\d]", "", phone_number)

        if phone_number.startswith("9") and len(phone_number) == 10:
            phone_number = "0" + phone_number

        if not re.match(r"^(09)\d{9}$", phone_number):
            raise ValidationError("شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد.")

        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("کاربری با این شماره تلفن از قبل وجود دارد.")

        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("رمز عبور و تکرار آن مطابقت ندارند.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminForm
    add_form = CustomUserCreationForm

    list_display = ("phone_number", "full_name", "is_staff", "is_active", "date_joined")
    search_fields = ("phone_number", "full_name")
    ordering = ("phone_number",)
    list_filter = ("is_active", "is_staff", "is_superuser")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("اطلاعات شخصی", {"fields": ("full_name",)}),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("تاریخ‌های مهم", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "full_name", "password1", "password2"),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")
