#!/bin/sh
set -e

echo "Aguardando PostgreSQL..."
while ! python - <<'EOF'
import os
import psycopg2

try:
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'petshop_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
        connect_timeout=2
    )
    conn.close()
    exit(0)
except Exception:
    exit(1)
EOF
do
  sleep 1
done

echo "PostgreSQL pronto."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

echo "Iniciando Gunicorn..."
exec "$@"
