from base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'citystats', # MUST BE SAME AS IN LOCAL.PY OR FABRIC WILL FAIL
        'USER': 'citystatsadmin', # MUST BE SAME AS IN LOCAL.PY OR FABRIC WILL FAIL
        'PASSWORD': PROD_DATABASE_PASSWORD,
        'HOST': '',
        'PORT': '',
    }
}

