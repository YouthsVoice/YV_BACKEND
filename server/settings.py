from pathlib import Path
from datetime import timedelta
import os
import dj_database_url # type: ignore
from decouple import config # type: ignore
import boto3 # type: ignore

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Configuration
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
DB_URL = config("DB", default=None)

# Database Configuration
#DB_FILE = os.path.join(BASE_DIR, 'db.sqlite3') if os.name == 'nt' else '/tmp/db.sqlite3'
"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_FILE,
    }
}

# S3 Configuration for SQLite persistence
S3_BUCKET = "zappa-dnklfrh3g"
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    s3 = boto3.client('s3')
    
    def download_db():
        try:
            s3.download_file(S3_BUCKET, 'db.sqlite3', DB_FILE)
        except Exception as e:
            Path(DB_FILE).touch()

    def upload_db():
        try:
            s3.upload_file(DB_FILE, S3_BUCKET, 'db.sqlite3')
        except Exception as e:
            print(f"Upload error: {str(e)}")

    download_db()"""
# settings.py (simplified)
"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'neondb',  # Database name
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_8H2VDgCrToOS',
        'HOST': 'ep-small-recipe-a1u5ihpq-pooler.ap-southeast-1.aws.neon.tech',
        'PORT': 5432,  # Default PostgreSQL port
        'OPTIONS': {
            'sslmode': 'require',
        },
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    DATABASES = {
        'default': dj_database_url.parse(config('DB'))
    }
# Security
ALLOWED_HOSTS = ['*',
    'youthsvoice-env.eba-dnbsv7bi.ap-southeast-2.elasticbeanstalk.com',
    'youthsvoice.org',
    'www.youthsvoice.org',
    'localhost','.awsapprunner.com',
    '127.0.0.1'
]

# Application Definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'whitenoise.runserver_nostatic',
    'members',
    'events',
    'volunteers',
    'donation'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://youthsvoice.org",
    "https://www.youthsvoice.org"
]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# Authentication
AUTH_USER_MODEL = 'members.Member'
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'