web: gunicorn config.wsgi --log-file -
release: python manage.py migrate --no-input && python manage.py seed_data
