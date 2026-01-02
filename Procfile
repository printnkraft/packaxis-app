web: python manage.py migrate --noinput && python create_superuser.py && gunicorn packaxis_app.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
