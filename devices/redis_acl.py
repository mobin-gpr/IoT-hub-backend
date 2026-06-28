"""
Redis ACL management helper for device topics.

This module provides functions to cache device ACLs in Redis for EMQX authorization.
Redis key format: emqx:acl:{username}
Redis value format: Hash with numbered fields in EMQX ACL format
Format: HSET emqx:acl:{username} 1 "allow,all,publish,devices/{uuid}/topic" 2 "allow,all,subscribe,devices/{uuid}/topic"
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
        Full topic name in format: devices/{uuid}/{topic_name}
    """
    return f"devices/{uuid}/{topic_name}"


def cache_device_acl(device):
    """
    Cache device ACL in Redis as a hash in EMQX ACL format.

    Args:
        device: Device model instance
    """
    redis_client = get_redis_client()

    # Build ACL rules in EMQX format
    acl_rules = []
    index = 1

    # Process topics
    for topic in device.topics:
        topic_name = topic.get("name", "")
        actions = topic.get("actions", [])
        full_topic = build_topic_name(str(device.uuid), topic_name)

        for action in actions:
            if action in ["publish", "subscribe"]:
                acl_rule = f"allow,all,{action},{full_topic}"
                acl_rules.append((index, acl_rule))
                index += 1

    # Store in Redis as hash with key: emqx:acl:{username}
    # Format: HSET emqx:acl:{username} 1 "allow,all,publish,devices/{uuid}/topic" 2 "allow,all,subscribe,devices/{uuid}/topic"
    redis_key = f"emqx:acl:{device.username}"
    if acl_rules:
        for idx, rule in acl_rules:
            redis_client.hset(redis_key, str(idx), rule)
    else:
        # If no topics, clear the key
        redis_client.delete(redis_key)

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

    # Get all hash fields
    acl_data = redis_client.hgetall(redis_key)

    if acl_data:
        # Parse EMQX ACL format: "allow,all,{action},{topic}"
        pub_topics = []
        sub_topics = []

        for idx, rule in acl_data.items():
            parts = rule.split(",")
            if len(parts) >= 4:
                action = parts[2]
                topic = parts[3]
                if action == "publish":
                    pub_topics.append(topic)
                elif action == "subscribe":
                    sub_topics.append(topic)

        return {
            "pub": pub_topics,
            "sub": sub_topics
        }

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
