from .settings import *


ALLOWED_HOSTS = ['transactions', 'localhost', '127.0.0.1']
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