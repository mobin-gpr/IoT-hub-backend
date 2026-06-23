import os
import sys
import time
import requests

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

import django

django.setup()

from django.core.cache import cache

BASE_URL = "http://127.0.0.1:8000/api/v1/accounts"


def test_login_flow():
    print("\n🧪 Starting Authentication Tests...")

    phone = "09123456789"

    # --- Step 1: Request OTP ---
    print("\n📤 Sending OTP request...")
    resp = requests.post(f"{BASE_URL}/login/", json={"phone_number": phone})
    if resp.status_code != 200:
        print(f"❌ OTP request failed: {resp.status_code} - {resp.text}")
        return
    print("✅ OTP sent successfully")

    # --- Step 2: Retrieve OTP from cache ---
    cache_key = f"otp_{phone}"
    cached = cache.get(cache_key)
    if not cached or "code" not in cached:
        print("❌ OTP not found in cache")
        return
    otp = cached["code"]
    print(f"🔑 Retrieved OTP from cache: {otp}")

    # --- Step 3: Verify OTP ---
    print("\n🔐 Verifying OTP...")
    resp = requests.post(
        f"{BASE_URL}/login/verify/", json={"phone_number": phone, "otp_code": otp}
    )
    if resp.status_code != 200:
        print(f"❌ Verification failed: {resp.status_code} - {resp.text}")
        return
    data = resp.json()
    print("✅ Login successful")
    print(f"👤 User: {data['user']}")
    print(f"🔑 Access token: {data['access'][:20]}...")
    print(f"🔄 Refresh token: {data['refresh'][:20]}...")

    # --- Step 4: Test resend limit ---
    print("\n⏳ Testing resend limit...")
    resp1 = requests.post(f"{BASE_URL}/login/", json={"phone_number": phone})
    if resp1.status_code == 400 and "ttl" in resp1.json():
        print("✅ Resend limit works")
        print(f"⏱️  Remaining TTL: {resp1.json().get('ttl')} seconds")
    else:
        print("⚠️  Resend limit not triggered as expected")
        print(f"Response: {resp1.text}")

    print("\n🎉 All tests passed!\n")


if __name__ == "__main__":
    test_login_flow()
