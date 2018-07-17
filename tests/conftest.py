# coding: utf-8
from django.conf import settings


# Minimum settings required for the app's tests.
SETTINGS_DICT = {
    'INSTALLED_APPS': (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',

        'vinaigrette',
    ),
    'USE_I18N': True,
    'LANGUAGES': (
        ('en', u'English'),
        ('fr', u'Français'),
    ),
    'LANGUAGE_CODE': 'en',
    'ROOT_URLCONF': 'urls',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    },
    'MIDDLEWARE': [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ],
    'SITE_ID': 1,
    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
        },
    ],
}


def pytest_configure():
    settings.configure(**SETTINGS_DICT)
