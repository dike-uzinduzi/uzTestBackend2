import os
from pathlib import Path
from decouple import config
import dj_database_url

# -----------------------------
# 📌 PATHS & CORE CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['uztestbackend2.onrender.com', 'localhost', '127.0.0.1', 'uztestbackend2-dv55.onrender.com']

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
    'whitenoise.runserver_nostatic',  # <-- ADDED for Whitenoise static file serving
    'django.contrib.staticfiles',

    # Local apps
    'users.apps.UsersConfig',
    'albums.apps.AlbumsConfig',
    'payments.apps.PaymentsConfig',
    'notifications.apps.NotificationsConfig',
]

# -----------------------------
# 📌 MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- ADDED for Whitenoise
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
# <-- UPDATED for security and production readiness
# This configuration relies solely on the DATABASE_URL environment variable
# provided by your hosting service (e.g., Render).
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # Specifies the database backend
#         'NAME': 'uzi',                      # Name of the database
#         'USER': 'postgres',                    # Username for database access
#         'PASSWORD': 'pz42uN2BBV',                  # Password for the user
#         'HOST': 'localhost',                       # Database host (e.g., 'localhost', 'db.example.com')
#         'PORT': '5432',                            # Port the database is listening on
#     }
# }

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),#os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # <-- ADDED for Whitenoise

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# -----------------------------
# 📌 AUTH
# -----------------------------
AUTH_USER_MODEL = 'users.UserAccount'
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend', 
    'django.contrib.auth.backends.ModelBackend',
]

# -----------------------------
# 📌 CORS CONFIG
# -----------------------------
# The origin of your Angular app (e.g., http://localhost:4200) must be in this list.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "https://app.uzinduziafrica.com",
]

# This MUST be set to True to allow the browser to send cookies.
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    # "https://uztestbackend2.onrender.com",
    # "https://www.uztestbackend2.onrender.com",
    "https://uztestbackend2-dv55.onrender.com",
]

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
# 📌 EMAIL CONFIG
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
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
        'user_create': 'users.serializers.CustomUserCreateSerializer',
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

# -----------------------------
# 📌 ADMINS
# -----------------------------
ADMINS = [
    ('Admin', 'dike@uzinduziafrica.com'),
]