from base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y8-(pab-igq&4n&q@5((vn_&jlty!m8$jsy@3qwokx68wq=r65'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'citystats',
        'USER': 'citystatsadmin',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

