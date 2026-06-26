#!/usr/bin/env python
"""
Test script for EMQX device authentication.
Creates a test device first, then attempts MQTT connection.
"""

import json
import os
import requests
import paho.mqtt.client as mqtt
import time
import sys

# Configuration
DJANGO_API_URL = "http://web:8000/api/v1/devices/create"
EMQX_HOST = "emqx"
EMQX_PORT = 1883
TEST_USERNAME = "sensor_01"
TEST_PASSWORD = ""  # Will be filled after creation

# Get token from environment or prompt
AUTH_TOKEN = os.environ.get("TEST_AUTH_TOKEN")
if not AUTH_TOKEN:
    print("⚠️  No TEST_AUTH_TOKEN environment variable found.")
    print("Please provide a valid JWT token (for a superuser or device creator):")
    AUTH_TOKEN = input("Token: ").strip()
    if not AUTH_TOKEN:
        print("❌ No token provided. Exiting.")
        sys.exit(1)


def create_device():
    """Create a test device via Django API."""
    payload = {
        "name": "Test Sensor",
        "model": "ESP32",
        "username": TEST_USERNAME,
        "is_active": True,
    }

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
    }

    print("📡 Creating test device...")
    print(f"   Username: {TEST_USERNAME}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)

    try:
        response = requests.post(DJANGO_API_URL, json=payload, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            device = data.get("device", {})
            plain_password = device.get("plain_password", "")
            print(f"   ✅ Device created with password: {plain_password}")
            return plain_password
        else:
            print(f"   ❌ Failed to create device: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def on_connect(client, userdata, flags, rc):
    """Callback when connecting to EMQX."""
    if rc == 0:
        print("\n✅ Connected successfully to EMQX")
        client.connected_flag = True
    else:
        print(f"\n❌ Failed to connect with code: {rc}")
        client.connected_flag = False


def test_mqtt_connection(username, password):
    """Test MQTT connection with given credentials."""
    print(f"\n🔐 Testing authentication for device: {username}")
    print(f"   Host: {EMQX_HOST}:{EMQX_PORT}")
    print(f"   Password: {password}")
    print("-" * 50)

    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.connected_flag = False
    client.on_connect = on_connect

    try:
        client.connect(EMQX_HOST, EMQX_PORT, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()

        if client.connected_flag:
            result = {"result": "allow", "message": "Connection successful"}
        else:
            result = {"result": "deny", "message": "Connection failed"}
    except Exception as e:
        result = {"result": "deny", "error": str(e)}

    print("\n📋 Auth Result:")
    print(json.dumps(result, indent=2))
    return result


def main():
    print("=" * 60)
    print("🧪 EMQX Device Authentication Test (Auto-Create)")
    print("=" * 60)

    # Step 1: Create device
    password = create_device()
    if not password:
        print("\n❌ Cannot proceed without device creation.")
        sys.exit(1)

    # Step 2: Test MQTT connection
    test_mqtt_connection(TEST_USERNAME, password)


if __name__ == "__main__":
    main()