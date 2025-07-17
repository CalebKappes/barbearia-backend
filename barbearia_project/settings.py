# barbearia_project/settings.py

import os
import dj_database_url
from pathlib import Path
from decouple import config
import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente de um arquivo .env em desenvolvimento
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# SECRET_KEY agora vem de uma variável de ambienteF
SECRET_KEY = config('SECRET_KEY')

# DEBUG agora vem de uma variável de ambiente
# O 'False' é o padrão se a variável não for encontrada (mais seguro)
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]

ALLOWED_HOSTS = []

# Adicionaremos nossa URL de produção aqui depois
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
# ... (o resto de INSTALLED_APPS fica como está) ...


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'barbearia_project.urls'

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

WSGI_APPLICATION = 'barbearia_project.wsgi.application'


# barbearia_project/settings.py

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# barbearia_project/settings.py

# ... (resto das suas configurações) ...

# Configurações do Django REST Framework
# Substitua o dicionário REST_FRAMEWORK antigo por este:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
# --- Configuração Final de CORS ---

# Para desenvolvimento local, permita o acesso do React
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
# Para produção, use a variável de ambiente
else:
    CORS_ALLOWED_ORIGINS_STR = os.getenv('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_STR.split(',') if CORS_ALLOWED_ORIGINS_STR else []


# Permite que o navegador envie cookies/credenciais (importante para o futuro).
CORS_ALLOW_CREDENTIALS = True

# Permite cabeçalhos específicos necessários para a nossa API.
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
# Adicione estas linhas para produção com o WhiteNoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ... (o resto das configurações como CORS_... e REST_FRAMEWORK...)
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# settings.py
# ... no final do arquivo ...

# Configurações de E-mail com SendGrid
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# A sua chave de API será lida de uma variável de ambiente
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# E-mail que aparecerá como remetente
SENDGRID_FROM_EMAIL = "sherlockbarberapp@gmail.com"
# settings.py (no final do arquivo)
CRON_SECRET_KEY = os.getenv("CRON_SECRET_KEY")
# settings.py

# ... todo o resto do seu arquivo ...

# Designa nosso modelo customizado como o padrão para autenticação
AUTH_USER_MODEL = 'core.Usuario'
# settings.py

# ... (outras configurações) ...

# --- CONFIGURAÇÕES DE E-MAIL (SENDGRID) ---
# Lendo as variáveis do nosso arquivo .env
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
SENDGRID_FROM_EMAIL = config('SENDGRID_FROM_EMAIL', default='')

# Configuração do serviço de e-mail do Django
if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'  # Esta palavra é literal, não mude
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY