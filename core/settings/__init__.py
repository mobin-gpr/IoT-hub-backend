"""
Settings package for core project.

Environment detection and settings module selection.
"""

import os

# Determine which settings module to load based on DJANGO_ENV
# Default to development if not set
environment = os.environ.get("DJANGO_ENV", "development")

if environment == "production":
    from .production import *
else:
    from .development import *

# For backward compatibility, expose BASE_DIR
from .base import BASE_DIR
