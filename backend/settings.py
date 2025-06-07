import sys
import dj_database_url
from os import getenv, path
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
 
dotenv_file=BASE_DIR / '.env.local'

if Path.is_file(dotenv_file):
    dotenv.load_dotenv(dotenv_file  )

DEVELOPMENT_MODE=getenv('DEVELOPMENT_MODE','False')=='True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CustomJWTAuthentication',
        ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

INSTALLED_APPS = [
    'djoser',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'storages',
    'social_django',
    'users',
    'albums',
    'artists',
   
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


if DEVELOPMENT_MODE is True:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # This will create a file db.sqlite3 in your project root
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

if DEVELOPMENT_MODE is True:
    STATIC_URL =  'static/'
    STATIC_ROOT=BASE_DIR / 'static/'
    MEDIA_URL='media/'
    MEDIA_ROOT=BASE_DIR / 'media/'
else:
    STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'STATICFILES_STORAGE':'storages.backends.s3.S3Storage'
          },

                                                                                                       
}
AUTHENTICATION_BACKENDS=[
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]
# Email settings
"""
EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = getenv('AWS_SES_FROM_EMAIL')

AWS_SES_ACCESS_KEY_ID = getenv('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = getenv('AWS_SES_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = getenv('AWS_SES_REGION_NAME')
AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
AWS_SES_FROM_EMAIL = getenv('AWS_SES_FROM_EMAIL')
USE_SES_V2 = True
"""
DOMAIN=getenv('DOMAIN')
SITE_NAME='Uzinduzi Africa'

"""
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = config["DEFAULT_FROM_EMAIL"]
EMAIL_HOST_USER = config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = config["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = False
"""
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"  
EMAIL_HOST_PASSWORD = "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"  # Your SendGrid API Key

DEFAULT_FROM_EMAIL = "dike@uzinduziafrica.com" 
DJOSER = {
    
    'PASSWORD_RESET_CONFIRM_URL': 'password-reset/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL':True,
    "SEND_CONFIRMATION_EMAIL": True,
    'ACTIVATION_URL': 'activation/{uid}/{token}',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'TOKEN_MODEL': None,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': getenv('REDIRECT_URLS').split(','),
    'SERIALIZERS': {
        'user': 'users.serializers.CustomUserSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',}
    
}

AUTH_COOKIE = 'access'
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24
AUTH_COOKIE_SECURE = getenv('AUTH_COOKIE_SECURE', 'True') == 'True'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = 'None'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = getenv('GOOGLE_AUTH_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = getenv('GOOGLE_AUTH_SECRET_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['first_name', 'last_name']

SOCIAL_AUTH_FACEBOOK_KEY = getenv('FACEBOOK_AUTH_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = getenv('FACEBOOK_AUTH_SECRET_KEY')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'email, first_name, last_name'
}

CORS_ALLOWED_ORIGINS = getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:4200'
).split(',')
CORS_ALLOW_CREDENTIALS = True



PESEPAY_INTEGRATION_KEY = 'f38b03198fbc4957b948cd912ae7521b'
PESEPAY_ENCRYPTION_KEY = '12e2d157-c120-40cd-aae3-6c5039675cad'
PESEPAY_RESULT_URL = 'http://localhost:4200/dashboard/payment/result'
PESEPAY_RETURN_URL = 'http://localhost:4200/dashboard/payment/return'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.UserAccount'
