#!/usr/bin/env python
"""
Simple MQTT connection test to EMQX.
"""

import paho.mqtt.client as mqtt
import time

# ========== Settings ==========
MQTT_HOST = "emqx"  # ← اسم سرویس در Docker
MQTT_PORT = 1883  # ← پورت داخلی
MQTT_USERNAME = "bobol"  # ← یوزرنیم دستگاه
MQTT_PASSWORD = "yz99go5qMpVPNzF$"  # ← پسورد دستگاه
# =============================


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected successfully to EMQX")
    else:
        print(f"❌ Connection failed with code: {rc}")


def main():
    print(f"🔌 Connecting to {MQTT_HOST}:{MQTT_PORT}")
    print(f"   Username: {MQTT_USERNAME}")
    print(f"   Password: {MQTT_PASSWORD[:4]}****")
    print("-" * 40)

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
