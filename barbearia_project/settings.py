# barbearia_project/settings.py

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente de um arquivo .env em desenvolvimento
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# SECRET_KEY agora vem de uma variável de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")

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

# Substitua toda a sua configuração de DATABASES por esta:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Se a URL for de um banco de dados PostgreSQL (como na Render)
    if DATABASE_URL.startswith('postgres://'):
        DATABASES['default'] = dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    else: # Para outros bancos de dados como o sqlite do nosso arquivo .env
        DATABASES['default'] = dj_database_url.config()
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
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
# barbearia_project/settings.py

# --- Configuração Final de CORS ---

# Pega a lista de URLs permitidas da variável de ambiente.
# O valor na Render deve ser: https://barbearia-frontend-snowy.vercel.app,http://localhost:3000
# O .split(',') transforma a string em uma lista Python.
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
# ...

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