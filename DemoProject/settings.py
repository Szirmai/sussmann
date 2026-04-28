from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-d-f$$@1t$f7ev)$bg=%$=u4&z12q-a4i%ke$=#lb!db#l56yr^'

DEBUG = False

ALLOWED_HOSTS = [
    'sussmann.hu',
    'www.sussmann.hu',
    '127.0.0.1',
    'localhost',
]

GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'Home',
    'shop',
    'dashboard',
    'analytics.apps.AnalyticsConfig',
    'bussiness',

    'django_recaptcha',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'analytics.middleware.PageViewMiddleware',
]

ROOT_URLCONF = 'DemoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'Home.context_processors.subscribe_form',
                'Home.context_processors.analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'DemoProject.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]




STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SESSION_COOKIE_AGE = 7 * 24 * 60 * 60  # 7 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


STRIPE_PUBLISHABLE_KEY = 'pk_test_51OBNQZHiouEL49qYRe08ptSiRvuQnlq0RMKvffjRJywta2sOmRmADtsfZZTkOf5p1Bji5mo0SfVIn8gW6tegATNQ0069Pm1PCN'
STRIPE_SECRET_KEY = 'sk_test_51OBNQZHiouEL49qYi7zsDvVqD97vKFUQeih4eTo2DdrgqpGCG6fUc9Pvd5lENCeA5oXs2H49pS5sXCTxoWoAFItg00tJ3PvYQt'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.sussmann.hu"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "noreply@sussmann.hu"
EMAIL_HOST_PASSWORD = "NoReply01234"
DEFAULT_FROM_EMAIL = "noreply@sussmann.hu"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'analytics-cache',
    }
}

RECAPTCHA_PUBLIC_KEY = "6Lcyjs4sAAAAALOeLsWjJtPZL8BEZQm0bhT9ZBt3"
RECAPTCHA_PRIVATE_KEY = "6Lcyjs4sAAAAAMh6uSXFIbmPCz-IBH08ZJJw6IZN"