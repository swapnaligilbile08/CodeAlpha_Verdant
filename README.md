# Verdant — Plant Store

A Django plant shop: catalog, cart, checkout, order history, accounts,
password reset.

## Setup

python -m venv venv

source venv/Scripts/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py seed_data

python manage.py createsuperuser

python manage.py 
runserver

Then visit localhost:8000 (admin at /admin/).

## Tests

python manage.py test store

## Deploy

Prod settings live in `config/settings/prod.py`. Needs `DJANGO_SECRET_KEY` and
`DJANGO_ALLOWED_HOSTS` set as environment variables, and the `Procfile` handles
migrations + seeding on release.