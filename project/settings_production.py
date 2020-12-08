import os
from project.settings import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': '5432'
    }
}

ALLOWED_HOSTS = []

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE_DEBUG = False

HOST = ''

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

ALLOWED_HOSTS = ['team-beat.herokuapp.com', 'herokuapp.com', 'www.team-beat.app']
