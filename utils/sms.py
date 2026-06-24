import logging
from accounts.tasks import send_verification_code_task

logger = logging.getLogger(__name__)


def send_verification_code(phone_number, code):
    """
    Send verification code via SMS using Celery task.
    This function is kept for backward compatibility with views.
    """
    try:
        send_verification_code_task.delay(phone_number, code)
        logger.info(f"SMS task queued for {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue SMS task for {phone_number}: {e}")
        return False
