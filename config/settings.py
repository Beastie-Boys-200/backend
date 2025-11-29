import os
import warnings
from pathlib import Path
from datetime import timedelta

warnings.filterwarnings('ignore', module='allauth.account.app_settings')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

def get_allowed_hosts():
    hosts_str = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    hosts = [host.strip().strip('"').strip("'") for host in hosts_str.split(',') if host.strip()]

    if DEBUG:
        dev_domain = os.environ.get('DEV_DOMAIN', '.hack.org')
        dev_ip_range = os.environ.get('DEV_IP_RANGE', '10.10.10')
        hosts.append(dev_domain)

        ip_range_limit = int(os.environ.get('DEV_IP_RANGE_LIMIT', '255'))
        for i in range(1, ip_range_limit):
            ip = f'{dev_ip_range}.{i}'
            if ip not in hosts:
                hosts.append(ip)
    return hosts

ALLOWED_HOSTS = get_allowed_hosts()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'apps.accounts',
    'apps.chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# БД
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import re
    match = re.match(r'postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': match.group(5),
                'USER': match.group(1),
                'PASSWORD': match.group(2),
                'HOST': match.group(3),
                'PORT': match.group(4),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель юзера
AUTH_USER_MODEL = 'accounts.User'

SITE_ID = 1

# CORS
def get_cors_settings():
    origins_str = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000')
    allowed_origins = [origin.strip() for origin in origins_str.split(',') if origin.strip()]

    dev_ip_range = os.environ.get('DEV_IP_RANGE', '10.10.10')
    dev_domain = os.environ.get('DEV_DOMAIN', '.hack.org')

    ip_pattern = dev_ip_range.replace('.', r'\.')
    origin_regexes = [
        rf"^https?://{ip_pattern}\.\d+:\d+$",
        rf"^https?://.*{dev_domain}:\d+$",
        r"^https?://localhost:\d+$",
        r"^https?://127\.0\.0\.1:\d+$",
    ]
    return allowed_origins, origin_regexes

CORS_ALLOWED_ORIGINS, CORS_ALLOWED_ORIGIN_REGEXES = get_cors_settings()
CORS_ALLOW_CREDENTIALS = True

# CSRF - allow cross-origin requests from frontend
def get_csrf_trusted_origins():
    origins = list(CORS_ALLOWED_ORIGINS)

    # Add localhost and 127.0.0.1 with common ports
    for host in ['localhost', '127.0.0.1', '0.0.0.0']:
        for port in [3000, 8000, 80, 443]:
            origins.append(f'http://{host}:{port}')
            origins.append(f'https://{host}:{port}')

    # Add all .hack.org subdomains with common ports
    dev_domain = os.environ.get('DEV_DOMAIN', '.hack.org')
    if dev_domain.startswith('.'):
        dev_domain = dev_domain[1:]

    # Get list of known subdomains from FRONTEND_URLS
    frontend_urls = os.environ.get('FRONTEND_URLS', '').split(',')
    for url in frontend_urls:
        url = url.strip()
        if url:
            origins.append(url.replace(':3000', ':8000'))  # Add backend port variant
            origins.append(url)  # Add frontend port

    # Add IP range
    dev_ip_range = os.environ.get('DEV_IP_RANGE', '10.10.10')
    for i in range(1, 20):  # First 20 IPs
        for port in [3000, 8000, 80]:
            origins.append(f'http://{dev_ip_range}.{i}:{port}')

    # Remove duplicates
    return list(set(origins))

CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins()

# Session and CSRF Cookie settings for same-site (HTTP)
# Note: SameSite=None requires HTTPS. For HTTP use 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'  # Lax for HTTP (None requires HTTPS)
SESSION_COOKIE_SECURE = False     # False for HTTP, True for HTTPS
SESSION_COOKIE_HTTPONLY = True    # Keep httponly for security
SESSION_COOKIE_DOMAIN = None      # None allows cookies to work per-domain
CSRF_COOKIE_SAMESITE = 'Lax'      # Lax for HTTP (None requires HTTPS)
CSRF_COOKIE_SECURE = False        # False for HTTP, True for HTTPS
CSRF_COOKIE_HTTPONLY = False      # Must be False so JS can read it
CSRF_COOKIE_DOMAIN = None         # None allows cookies to work per-domain

# REST
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',  # Read JWT from cookies
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback to header
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'auth-token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh-token',
    'JWT_AUTH_HTTPONLY': False,  # False for development (allows cookies between different ports)
    'JWT_AUTH_SAMESITE': 'Lax',  # Lax for HTTP development (None requires HTTPS)
    'JWT_AUTH_SECURE': False,  # False for HTTP, set to True in production with HTTPS
    'USER_DETAILS_SERIALIZER': 'apps.accounts.serializers.UserSerializer',
    'REGISTER_SERIALIZER': 'apps.accounts.serializers.CustomRegisterSerializer',
    'LOGIN_SERIALIZER': 'apps.accounts.serializers.CustomLoginSerializer',
}

# Allauth - авторизация через email
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomAccountAdapter'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
