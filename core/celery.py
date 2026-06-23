"""
Celery configuration for core project.

This module defines the Celery app instance and loads tasks from all registered apps.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Create Celery app instance
app = Celery("core")

# Load configuration from Django settings
# Using namespace 'CELERY' means all celery config keys must start with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """A debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")
