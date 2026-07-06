#!/bin/sh
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting Bless Die CRM bot..."
exec python -m app.main
