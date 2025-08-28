import os
from pathlib import Path
from decouple import config

# -----------------------------
# 📌 PATHS & CORE CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']

# -----------------------------
# 📌 DJANGO REST FRAMEWORK
# -----------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# -----------------------------
# 📌 INSTALLED APPS
# -----------------------------
INSTALLED_APPS = [
    # Third-party
    'djoser',
    'rest_framework',
    'corsheaders',
    'storages',
    'social_django',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'users',
    'albums',
    'artists',
    'payments',
]

# -----------------------------
# 📌 MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------
# 📌 TEMPLATES
# -----------------------------
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

# -----------------------------
# 📌 DATABASE CONFIG
# -----------------------------
DB_ENGINE = config('ENGINE').strip()
DB_NAME = config('NAME')
DB_USER = config('USER')
DB_PASSWORD = config('PASSWORD')
DB_HOST = config('HOST')
DB_PORT = config('PORT')

print(f"🔥 ENGINE SET TO: '{DB_ENGINE}'")

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# -----------------------------
# 📌 PASSWORD VALIDATORS
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# 📌 LOCALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# 📌 STATIC & MEDIA
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'


# -----------------------------
# 📌 AUTH
# -----------------------------
AUTH_USER_MODEL = 'users.UserAccount'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    
]

# -----------------------------
# 📌 CORS CONFIG
# -----------------------------
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 'https://app.uzinduziafrica.com'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# -----------------------------
# 📌 COOKIE CONFIG
# -----------------------------
AUTH_COOKIE = 'access'
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24
AUTH_COOKIE_SECURE = config('AUTH_COOKIE_SECURE', 'True') == 'True'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = 'None'

# -----------------------------
# 📌 EMAIL CONFIG — SENDGRID

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')



# -----------------------------
# 📌 DJOSER CONFIG
# -----------------------------
DJOSER = {
    'SERIALIZERS': {
        #'user_create': 'core.serializers.UserCreateSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',
        'user': 'users.serializers.CustomUserSerializer',
    },
     'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': 'activation/{uid}/{token}',
     'USER_CREATE_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
     'TOKEN_MODEL': None,
     'PASSWORD_RESET_CONFIRM_URL': 'password-reset/{uid}/{token}',
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
}



# -----------------------------
# 📌 PESEPAY CONFIG
# -----------------------------
PESEPAY_INTEGRATION_KEY = config('PESEPAY_INTEGRATION_KEY')
PESEPAY_ENCRYPTION_KEY = config('PESEPAY_ENCRYPTION_KEY')
PESEPAY_RETURN_URL = config('PESEPAY_RETURN_URL')
PESEPAY_RESULT_URL = config('PESEPAY_RESULT_URL')

# -----------------------------
# 📌 APP DOMAIN
# -----------------------------
DOMAIN = config('DOMAIN')
SITE_NAME = 'Uzinduzi Africa'

# -----------------------------
# 📌 DEFAULT PK FIELD
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
