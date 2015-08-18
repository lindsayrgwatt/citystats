from base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'citystats',
        'USER': 'citystatsadmin',
        'PASSWORD': LOCAL_DATABASE_PASSWORD,
        'HOST': '',
        'PORT': '',
    }
}

