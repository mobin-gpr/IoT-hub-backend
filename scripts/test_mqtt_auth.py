import paho.mqtt.client as mqtt
import time
import sys

MQTT_HOST = "emqx"
MQTT_PORT = 1883

CORRECT_USER = "bobol"
CORRECT_PASS = "yz99go5qMpVPNzF$"

WRONG_USER = "bobol"
WRONG_PASS = "wrong_password"

WRONG_USER2 = "nonexistent"
WRONG_PASS2 = "test123"

results = []


def test_connect(label, username, password, expect_allow):
    print(f"\n--- Test: {label} ---")
    print(f"  Username: {username}")
    print(f"  Password: {password[:4] if password else ''}***")
    print(f"  Expected: {'allow' if expect_allow else 'deny'}")

    connected = [False]

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            connected[0] = True

    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"  Error: {e}")

    result = "allow" if connected[0] else "deny"
    passed = connected[0] == expect_allow
    status = "PASS" if passed else "FAIL"
    icon = "✅" if passed else "❌"
    print(f"  Result: {result} -> {icon} {status}")
    results.append((label, result, passed))


def main():
    print("=" * 60)
    print("MQTT Device Authentication Test")
    print("=" * 60)

    test_connect("Correct credentials", CORRECT_USER, CORRECT_PASS, expect_allow=True)
    test_connect("Wrong password", WRONG_USER, WRONG_PASS, expect_allow=False)
    test_connect("Wrong username", WRONG_USER2, WRONG_PASS2, expect_allow=False)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    all_pass = True
    for label, result, passed in results:
        icon = "✅" if passed else "❌"
        all_pass = all_pass and passed
        print(f"  {icon} {label}: {result}")
    print("=" * 60)
    print(f"Overall: {'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
