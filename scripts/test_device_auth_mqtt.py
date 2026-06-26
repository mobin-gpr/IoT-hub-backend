#!/usr/bin/env python
"""
Complete test script for EMQX device authentication.
- Auto-creates a test user if not exists
- Auto-login via OTP (reads OTP from Django cache)
- Creates a test device
- Tests MQTT connection with correct and wrong passwords
"""

import json
import subprocess
import requests
import paho.mqtt.client as mqtt
import time
import sys
import os

# Django setup for creating user
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache

# ============================================================
# CONFIGURATION
# ============================================================
DJANGO_BASE_URL = "http://web:8000/api/v1"
OTP_LOGIN_URL = f"{DJANGO_BASE_URL}/accounts/login/"
OTP_VERIFY_URL = f"{DJANGO_BASE_URL}/accounts/login/verify/"
DEVICE_CREATE_URL = f"{DJANGO_BASE_URL}/devices/create"
EMQX_HOST = "emqx"
EMQX_PORT = 1883

TEST_PHONE = "09123456789"
TEST_USERNAME = "sensor_01"
# ============================================================

User = get_user_model()


def create_test_user():
    """Create a test user if not exists."""
    print("👤 Creating test user...")
    print("-" * 50)

    user, created = User.objects.get_or_create(
        phone_number=TEST_PHONE,
        defaults={
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "is_approved": True,
        },
    )

    if created:
        print(f"✅ User created: {TEST_PHONE}")
    else:
        print(f"✅ User already exists: {TEST_PHONE}")

    return user


def get_otp_from_cache(phone_number):
    """Read OTP from Django cache."""
    data = cache.get(f"otp_{phone_number}")
    if data and isinstance(data, dict):
        return data.get("code")
    return None


def get_access_token(phone_number):
    """Login via OTP and get access token."""
    print("\n📱 Logging in...")
    print("-" * 50)

    # Step 1: Request OTP
    print("📤 Requesting OTP...")
    try:
        resp = requests.post(
            OTP_LOGIN_URL, json={"phone_number": phone_number}, timeout=5
        )
        if resp.status_code != 200:
            print(f"❌ OTP request failed: {resp.status_code} - {resp.text}")
            return None
        print("✅ OTP sent")
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    # Step 2: Get OTP from cache
    print("📖 Reading OTP from cache...")
    otp_code = get_otp_from_cache(phone_number)
    if not otp_code:
        print("❌ OTP not found in cache")
        return None
    print(f"✅ OTP: {otp_code}")

    # Step 3: Verify OTP
    print("🔐 Verifying OTP...")
    try:
        resp = requests.post(
            OTP_VERIFY_URL,
            json={"phone_number": phone_number, "otp_code": otp_code},
            timeout=5,
        )
        if resp.status_code != 200:
            print(f"❌ Verification failed: {resp.status_code} - {resp.text}")
            return None

        data = resp.json()
        token = data.get("access")
        if token:
            print("✅ Access token obtained")
            return token
        print(f"❌ No token in response: {data}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def create_device(access_token):
    """Create a test device."""
    payload = {
        "name": "Test Sensor",
        "model": "ESP32",
        "username": TEST_USERNAME,
        "is_active": True,
    }

    print(f"\n📡 Creating device: {TEST_USERNAME}")
    print("-" * 50)

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        resp = requests.post(
            DEVICE_CREATE_URL, json=payload, headers=headers, timeout=5
        )
        print(f"   Status: {resp.status_code}")

        if resp.status_code == 201:
            data = resp.json()
            device = data.get("device", {})
            password = device.get("plain_password", "")
            print(f"   ✅ Device created")
            print(f"   Password: {password}")
            return password
        else:
            print(f"   ❌ Failed: {resp.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_mqtt(username, password, expected=True):
    """Test MQTT connection."""
    label = "✅ ALLOW" if expected else "❌ DENY"
    print(f"\n🔐 Testing MQTT (expected: {label})")
    print(f"   Username: {username}")
    print(f"   Password: {password[:4]}****")
    print("-" * 40)

    client = mqtt.Client()
    client.username_pw_set(username, password)
    connected = False

    def on_connect(c, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            connected = True

    client.on_connect = on_connect

    try:
        client.connect(EMQX_HOST, EMQX_PORT, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()

        result = "allow" if connected else "deny"
        status = "✅ PASS" if (connected == expected) else "❌ FAIL"
        print(f"   Result: {result} {status}")
        return connected
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🧪 EMQX Device Authentication Test")
    print("=" * 60)

    # Step 1: Create user
    create_test_user()

    # Step 2: Login and get token
    token = get_access_token(TEST_PHONE)
    if not token:
        print("\n❌ Cannot proceed without token.")
        sys.exit(1)

    # Step 3: Create device
    password = create_device(token)
    if not password:
        print("\n❌ Cannot proceed without device.")
        sys.exit(1)

    # Step 4: Test MQTT with correct password
    test_mqtt(TEST_USERNAME, password, expected=True)

    # Step 5: Test MQTT with wrong password
    test_mqtt(TEST_USERNAME, "wrong_password", expected=False)

    print("\n" + "=" * 60)
    print("✅ Test complete!")


if __name__ == "__main__":
    main()
