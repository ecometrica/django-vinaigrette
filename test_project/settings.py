#encoding: utf-8

SECRET_KEY = "thisisasecretkeyfortests.itisverysecure"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'vinaigrette',

    'test_project.dressings',
)

USE_I18N = True
LANGUAGES = (
    ('en', u'English'),
    ('fr', u'Français'),
)
LOCALE_PATHS = (
    'locale',
)

LANGUAGE_CODE = 'en'
ROOT_URLCONF = 'test_project.urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

SITE_ID = 1
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
