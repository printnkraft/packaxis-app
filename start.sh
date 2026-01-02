#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting PackAxis deployment..."
echo "=========================================="

echo ""
echo "📊 Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed!"

echo ""
echo "👤 Creating/checking superuser..."
python create_superuser.py
echo "✅ Superuser ready!"

echo ""
echo "🌐 Starting Gunicorn web server..."
gunicorn packaxis_app.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
