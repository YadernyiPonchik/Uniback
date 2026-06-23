web: cd backend && gunicorn auth_system.wsgi:application --bind 0.0.0.0:$PORT
worker: cd backend && python manage.py bot
release: cd backend && python manage.py migrate --noinput
