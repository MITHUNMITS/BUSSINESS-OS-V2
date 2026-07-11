#!/usr/bin/env sh
set -eu

echo "Waiting for PostgreSQL at db:5432..."
until pg_isready -h db -p 5432 -U business_os -d business_os >/dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is ready."

case "${1:-web}" in
  web)
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  worker)
    exec celery -A business_os.config worker -l info
    ;;
  *)
    exec "$@"
    ;;
esac

