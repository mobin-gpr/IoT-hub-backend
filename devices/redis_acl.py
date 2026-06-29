"""
Redis ACL management helper for EMQX 5.7 Redis Authorization.

Redis key:
    emqx:acl:{username}

Redis hash format:
    field = topic
    value = publish | subscribe | pubsub

Example:
    HSET emqx:acl:test \
        "devices/<uuid>/status" publish \
        "devices/<uuid>/cmd" subscribe \
        "devices/<uuid>/config" pubsub
"""

import os


def get_redis_client():
    import redis

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)


def build_topic_name(uuid, topic_name):
    return f"devices/{uuid}/{topic_name}"


def cache_device_acl(device):
    redis_client = get_redis_client()

    redis_key = f"emqx:acl:{device.username}"

    pipe = redis_client.pipeline()

    # Remove previous ACL
    pipe.delete(redis_key)

    for topic in device.topics:
        topic_name = topic.get("name")
        actions = set(topic.get("actions", []))

        full_topic = build_topic_name(str(device.uuid), topic_name)

        if actions == {"publish", "subscribe"}:
            permission = "pubsub"
        elif "publish" in actions:
            permission = "publish"
        elif "subscribe" in actions:
            permission = "subscribe"
        else:
            continue

        pipe.hset(redis_key, full_topic, permission)

    pipe.execute()


def cache_all_device_acls():
    from devices.models import Device

    count = 0

    for device in Device.objects.all():
        cache_device_acl(device)
        count += 1

    return count


def get_device_acl(username):
    redis_client = get_redis_client()

    redis_key = f"emqx:acl:{username}"

    rules = redis_client.hgetall(redis_key)

    if not rules:
        return None

    publish = []
    subscribe = []

    for topic, permission in rules.items():
        if permission == "publish":
            publish.append(topic)
        elif permission == "subscribe":
            subscribe.append(topic)
        elif permission == "pubsub":
            publish.append(topic)
            subscribe.append(topic)

    return {
        "pub": sorted(publish),
        "sub": sorted(subscribe),
    }


def delete_device_acl(username):
    redis_client = get_redis_client()
    redis_client.delete(f"emqx:acl:{username}")