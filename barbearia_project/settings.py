# barbearia_project/settings.py

import os
import dj_database_url
from pathlib import Path
from decouple import config

# Carrega variáveis de ambiente de um arquivo .env em desenvolvimento
from dotenv import load_dotenv
load_dotenv() # O dotenv vai procurar o .env no diretório raiz automaticamente

# --- Configurações Principais ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config("DEBUG", default=False, cast=bool)
ROOT_URLCONF = 'barbearia_project.urls'
WSGI_APPLICATION = 'barbearia_project.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.Usuario' # Modelo de usuário customizado

# --- Hosts Permitidos ---
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- Aplicativos Instalados ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps de terceiros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Seu app
    'core',
]

# --- Middleware ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Deve vir antes da maioria dos outros
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Banco de Dados ---
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# --- Validadores de Senha ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- Arquivos Estáticos (CSS, JS, Imagens) ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Configurações do Django Rest Framework (API) ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # APENAS a autenticação por Token como padrão para a API.
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# --- Configurações de CORS (Cross-Origin Resource Sharing) ---
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    CORS_ALLOWED_ORIGINS_STR = os.getenv('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_STR.split(',') if CORS_ALLOWED_ORIGINS_STR else []

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# --- Configurações de Cookies (para produção) ---
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# --- Configurações de E-mail (SendGrid) ---
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
SENDGRID_FROM_EMAIL = config('SENDGRID_FROM_EMAIL', default='seu-email-aqui@exemplo.com')

if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY

# --- Chave Secreta para CRON Jobs ---
CRON_SECRET_KEY = config("CRON_SECRET_KEY", default='')
