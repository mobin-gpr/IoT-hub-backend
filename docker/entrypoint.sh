#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Caching device ACLs in Redis..."
python manage.py cache_device_acls || echo "Warning: cache_device_acls failed (Redis might be unavailable)"

echo "Starting application..."
exec "$@"
