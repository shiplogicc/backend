"""
Django settings for shiplogic project.

Generated by 'django-admin startproject' using Django 4.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=17dr46x97q0q3%ctmr$%f9=e+7hxkg0%$1x&ac&2^z=!k6d(g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://*.shiplogic.in"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True

# Application definition
SHARED_APPS = (
   'tenant_schemas',  # mandatory, should always be before any django app
   'tenant', # you must list the app where your tenant model resides in
   'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
   'authentication',
   'oauth2_provider',
   'location',
   'airwaybill',
   'api',
   'customer',
   'corsheaders',
   'servicecenter',
   'pickup',
   'slconfig',
   'integration_services',
   'billing',
   'gst',
)


TENANT_APPS = (
    'django.contrib.contenttypes',

   # your tenant-specific apps
   'tenant',
   'authentication',
   'location',
   'airwaybill',
   'api',
   'customer',
   'servicecenter',
   'pickup',
   'slconfig',
   'integration_services',
   'billing',
   'gst',
)


INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]





MIDDLEWARE = [
        'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shiplogic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shiplogic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
        'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME':'shiplogic',
        'USER':'shiplogic',
        'PASSWORD':'admin',
        'HOST':'localhost',
        }
}

DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter',
)
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
TENANT_MODEL = "tenant.Client" # app.Model

TENANT_DOMAIN_MODEL = "tenant.Domain"

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {

         # Use Django's standard django.contrib.auth permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
    # Uncomment following if you want to access the admin
]
OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'PKCE_REQUIRED':False,
    'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'},
    'OAUTH_DELETE_EXPIRED': True,
    #'ACCESS_TOKEN_GENERATOR' : 'Authentication.generators.random_token_generator',
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600000,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60,
    'CLIENT_SECRET_GENERATOR_LENGTH': 128,
    'ALLOWED_REDIRECT_URI_SCHEMES': ['http', 'https'],
}
