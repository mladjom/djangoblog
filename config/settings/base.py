from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjusted for nested structure

SECRET_KEY = 'django-insecure-)&0%+u6y(g9f7i4jh1ymmstpl)e=h*qu@e2gxjha+o6n)15i7^'

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

ROOT_URLCONF = 'config.urls'

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog.apps.BlogConfig',
    'graphene_django',
    'corsheaders',
    'django.contrib.sitemaps',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

# GraphQL
GRAPHENE = {
    "SCHEMA": "blog.schema.schema",
}

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = "en"
TIME_ZONE = 'Europe/Stockholm'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('sv', 'Swedish'),
    ('sr', 'Serbian'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Define STATIC_ROOT

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
