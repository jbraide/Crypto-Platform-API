from .settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nova_crypto',
        'USER': 'crypto_admin',
        'PASSWORD': 'novacryptotradingplatform',
        'HOST': 'db',
        'PORT': '5432',
    }
}