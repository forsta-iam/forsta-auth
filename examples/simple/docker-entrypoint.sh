#!/bin/sh -e

python manage.py collectstatic --no-input
python manage.py migrate

if [ -n "$FIXTURE" ] ; then
    python manage.py loaddata $FIXTURE
fi

gunicorn forsta_auth_simple.wsgi:application $@
