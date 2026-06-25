"""Utility functions for extracting device information from user agent strings."""

import re


def get_device_info(user_agent):
    """
    Extract device information from user agent string.

    Args:
        user_agent: User agent string from request

    Returns:
        dict: Device information including device_type, browser, os, device_name
    """
    user_agent_lower = user_agent.lower()

    # Detect device type
    device_type = "desktop"
    if "mobile" in user_agent_lower or "android" in user_agent_lower:
        device_type = "mobile"
    elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        device_type = "tablet"

    # Detect browser
    browser = "Unknown"
    if "chrome" in user_agent_lower and "edge" not in user_agent_lower:
        browser = "Chrome"
    elif "firefox" in user_agent_lower:
        browser = "Firefox"
    elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
        browser = "Safari"
    elif "edge" in user_agent_lower:
        browser = "Edge"
    elif "opera" in user_agent_lower:
        browser = "Opera"

    # Detect OS
    os = "Unknown"
    if "windows" in user_agent_lower:
        os = "Windows"
    elif "mac" in user_agent_lower:
        os = "macOS"
    elif "linux" in user_agent_lower:
        os = "Linux"
    elif "android" in user_agent_lower:
        os = "Android"
    elif (
        "ios" in user_agent_lower
        or "iphone" in user_agent_lower
        or "ipad" in user_agent_lower
    ):
        os = "iOS"

    # Generate device name
    device_name = f"{os} {browser} on {device_type}"

    return {
        "device_type": device_type,
        "browser": browser,
        "os": os,
        "device_name": device_name,
    }


def get_client_ip(request):
    """
    Get client IP address from request.

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
