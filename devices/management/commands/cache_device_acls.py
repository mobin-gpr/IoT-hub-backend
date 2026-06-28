"""
Django management command to cache all device ACLs in Redis.

This command is useful when Redis data is lost due to power outage or other issues.
It reads all devices from PostgreSQL and caches their ACLs in Redis for EMQX authorization.

Usage:
    python manage.py cache_device_acls
"""

from django.core.management.base import BaseCommand
from devices.redis_acl import cache_all_device_acls


class Command(BaseCommand):
    help = "Cache all device ACLs from PostgreSQL to Redis"

    def handle(self, *args, **options):
        """
        Execute the command to cache all device ACLs.
        """
        self.stdout.write(self.style.WARNING("Starting to cache all device ACLs..."))

        try:
            count = cache_all_device_acls()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully cached {count} device ACLs in Redis.")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error caching device ACLs: {str(e)}"))
            raise
