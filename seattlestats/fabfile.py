from fabric.api import local, env
from fabric.contrib import django
from seattlestats.settings.secrets import *

django.settings_module('seattlestats.settings.local')
from django.conf import settings

env.local_base_dir = settings.BASE_DIR
env.local_settings = "--settings=seattlestats.settings.local"
env.local_postgres_database = settings.DATABASES['default']['NAME']
env.local_postgres_user = settings.DATABASES['default']['USER']
env.local_postgres_password = LOCAL_DATABASE_PASSWORD

def print_local_settings():
    local("echo %(local_base_dir)s" % env)
    local("echo %(local_postgres_user)s" % env)
    local("echo %(local_postgres_password)s" % env)

def set_up_local_database():
    local("psql -c \"CREATE DATABASE %(local_postgres_database)s;\"" % env)
    local("psql -c \"CREATE USER %(local_postgres_user)s WITH PASSWORD '%(local_postgres_password)s';\"" % env)
    local("psql <<EOF\n\c %(local_postgres_database)s\nCREATE EXTENSION postgis;\nEOF" % env)
    local("psql <<EOF\n\c %(local_postgres_database)s\nCREATE EXTENSION postgis_topology;\nEOF" % env)
    local("psql -c \"GRANT ALL PRIVILEGES ON DATABASE %(local_postgres_database)s TO %(local_postgres_user)s;\"" % env)

def create_local_superuser():
    local("python manage.py createsuperuser %(local_settings)s" % env)

def runserver():
    local("python manage.py runserver %(local_settings)s" % env)
