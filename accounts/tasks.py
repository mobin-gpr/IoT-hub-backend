from celery import shared_task
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=5)
def send_verification_code_task(self, phone_number, code):
    """
    Celery task to send verification code via SMS.ir API.
    """
    try:
        api_key = getattr(settings, "SMS_API_KEY", None)

        # If no API key is configured, just log and skip (development mode)
        if not api_key or api_key.startswith("CIZ4"):
            logger.info(f"[MOCK] SMS to {phone_number}: code={code}")
            return {"status": "mock", "message": "SMS skipped (mock mode)"}

        url = settings.SMS_API_URL
        template_id = settings.SMS_TEMPLATE_ID

        payload = {
            "mobile": phone_number,
            "templateId": template_id,
            "parameters": [{"name": "code", "value": code}],
        }

        headers = {"Content-Type": "application/json", "x-api-key": api_key}

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(
                f"SMS sending failed: {response.status_code} - {response.text}"
            )
            raise self.retry(exc=Exception(f"SMS API error: {response.text}"))

        logger.info(f"SMS sent successfully to {phone_number}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception while sending SMS: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in SMS task: {e}")
        raise e
