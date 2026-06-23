import logging

logger = logging.getLogger(__name__)


def send_verification_code(phone_number, code):
    """
    Send verification code via SMS.
    Currently mocked for development - only logs the code.
    In production, integrate with SMS service provider.

    Args:
        phone_number (str): Recipient phone number (e.g., "09123456789")
        code (str): Verification code to send

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # TODO: Implement actual SMS sending logic
        # Example: use SMS.ir, Kaveh Negar, etc.
        logger.info(f"SMS verification code for {phone_number}: {code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {e}")
        return False
