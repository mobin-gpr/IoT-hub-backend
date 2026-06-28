"""
Redis ACL management helper for device topics.

This module provides functions to cache device ACLs in Redis for EMQX authorization.
Redis key format: emqx:acl:{username}
Redis value format: Hash with 'pub' and 'sub' fields containing JSON arrays
"""

import json
import os
from django.conf import settings


def get_redis_client():
    """
    Get Redis client instance.
    """
    import redis

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)


def build_topic_name(uuid, topic_name):
    """
    Build full topic name using device UUID and topic name.

    Args:
        uuid: Device UUID string
        topic_name: Topic name (e.g., 'status', 'event')

    Returns:
        Full topic name in format: {topic_name}_{uuid}
    """
    return f"{topic_name}_{uuid}"


def cache_device_acl(device):
    """
    Cache device ACL in Redis as a hash.

    Args:
        device: Device model instance
    """
    redis_client = get_redis_client()

    # Build ACL data
    pub_topics = []
    sub_topics = []

    # Process topics
    for topic in device.topics:
        topic_name = topic.get("name", "")
        actions = topic.get("actions", [])
        full_topic = build_topic_name(str(device.uuid), topic_name)

        if "publish" in actions:
            pub_topics.append(full_topic)
        if "subscribe" in actions:
            sub_topics.append(full_topic)

    # Store in Redis as hash with key: emqx:acl:{username}
    redis_key = f"emqx:acl:{device.username}"
    redis_client.hset(redis_key, "pub", json.dumps(pub_topics))
    redis_client.hset(redis_key, "sub", json.dumps(sub_topics))

    # Also set TTL (optional, adjust as needed)
    # redis_client.expire(redis_key, 86400)  # 24 hours


def cache_all_device_acls():
    """
    Cache all device ACLs in Redis.
    This is useful when Redis data is lost.

    Returns:
        Number of devices cached
    """
    from devices.models import Device

    devices = Device.objects.all()
    count = 0

    for device in devices:
        cache_device_acl(device)
        count += 1

    return count


def get_device_acl(username):
    """
    Get device ACL from Redis.

    Args:
        username: Device username

    Returns:
        ACL data dict with pub/sub lists, or None if not found
    """
    redis_client = get_redis_client()
    redis_key = f"emqx:acl:{username}"

    # Get hash fields
    pub_data = redis_client.hget(redis_key, "pub")
    sub_data = redis_client.hget(redis_key, "sub")

    if pub_data or sub_data:
        acl_data = {
            "pub": json.loads(pub_data) if pub_data else [],
            "sub": json.loads(sub_data) if sub_data else []
        }
        return acl_data

    return None


def delete_device_acl(username):
    """
    Delete device ACL from Redis.

    Args:
        username: Device username
    """
    redis_client = get_redis_client()
    redis_key = f"emqx:acl:{username}"
    redis_client.delete(redis_key)
