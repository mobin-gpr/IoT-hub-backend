"""Test script for session management features."""

import os
import sys
import requests

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
django_env = os.environ.get("DJANGO_ENV", "production")
if django_env == "production":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

import django

django.setup()

BASE_URL = "http://127.0.0.1:8000/api/v1/accounts"


def test_session_management():
    print("\n🧪 Starting Session Management Tests...")

    phone = "09987654321"

    # --- Step 1: Login and get token ---
    print("\n📤 Sending OTP request...")
    resp = requests.post(f"{BASE_URL}/login/", json={"phone_number": phone})
    if resp.status_code != 200:
        print(f"❌ OTP request failed: {resp.status_code} - {resp.text}")
        return
    print("✅ OTP sent successfully")

    # --- Step 2: Get OTP from cache ---
    from django.core.cache import cache

    cache_key = f"otp_{phone}"
    cached = cache.get(cache_key)
    if not cached or "code" not in cached:
        print("❌ OTP not found in cache")
        return
    otp = cached["code"]
    print(f"🔑 Retrieved OTP from cache: {otp}")

    # --- Step 3: Verify OTP and get tokens ---
    print("\n🔐 Verifying OTP...")
    resp = requests.post(
        f"{BASE_URL}/login/verify/", json={"phone_number": phone, "otp_code": otp}
    )
    if resp.status_code != 200:
        print(f"❌ Verification failed: {resp.status_code} - {resp.text}")
        return
    data = resp.json()
    access_token = data["access"]
    print("✅ Login successful")
    print(f"🔑 Access token: {access_token[:20]}...")

    headers = {"Authorization": f"Bearer {access_token}"}

    # --- Step 4: List sessions ---
    print("\n📋 Listing user sessions...")
    resp = requests.get(f"{BASE_URL}/sessions/", headers=headers)
    if resp.status_code != 200:
        print(f"❌ List sessions failed: {resp.status_code} - {resp.text}")
        return
    sessions = resp.json()
    print(f"✅ Found {len(sessions)} session(s)")
    for session in sessions:
        print(
            f"   - {session['device_name']} (ID: {session['id']}, Active: {session['is_active']})"
        )

    if not sessions:
        print("⚠️  No sessions found, skipping further tests")
        return

    # --- Step 5: Revoke a specific session ---
    session_id = sessions[0]["id"]
    print(f"\n🚫 Revoking session {session_id}...")
    resp = requests.delete(f"{BASE_URL}/sessions/{session_id}/", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Revoke session failed: {resp.status_code} - {resp.text}")
        return
    print("✅ Session revoked successfully")
    print(f"   Response: {resp.json()}")

    # --- Step 6: List sessions again to verify ---
    print("\n📋 Listing sessions after revoke...")
    resp = requests.get(f"{BASE_URL}/sessions/", headers=headers)
    if resp.status_code != 200:
        print(f"❌ List sessions failed: {resp.status_code} - {resp.text}")
        return
    sessions = resp.json()
    print(f"✅ Found {len(sessions)} session(s)")
    for session in sessions:
        print(
            f"   - {session['device_name']} (ID: {session['id']}, Active: {session['is_active']})"
        )

    # --- Step 7: Revoke all sessions except current ---
    print("\n🚫 Revoking all other sessions...")
    resp = requests.post(f"{BASE_URL}/sessions/revoke-all/", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Revoke all sessions failed: {resp.status_code} - {resp.text}")
        return
    print("✅ All other sessions revoked successfully")
    print(f"   Response: {resp.json()}")

    print("\n🎉 All session management tests passed!\n")


if __name__ == "__main__":
    test_session_management()
