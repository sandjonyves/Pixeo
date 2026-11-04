"""Configuration Django commune à tous les environnements Pixeo.

Les valeurs sensibles ou dépendantes de l'environnement sont lues depuis
`backend/.env` ou les variables d'environnement. Aucun secret n'est codé en dur.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ─── Sécurité de base ─────────────────────────────────────────────────────────
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# ─── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "apps.accounts",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ─── Base de données ──────────────────────────────────────────────────────────
# SQLite par défaut en développement. La production impose PostgreSQL via
# DATABASE_URL (voir production.py).
DATABASE_URL = env(
    "DATABASE_URL",
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
)
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=env.int("DATABASE_CONN_MAX_AGE", default=0),
    )
}
# Vérifie les connexions persistantes avant réutilisation. Sans effet lorsque
# CONN_MAX_AGE vaut 0 (nouvelle connexion à chaque requête).
if DATABASES["default"].get("CONN_MAX_AGE", 0):
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# ─── Authentification ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Fichiers statiques et médias ─────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / env("MEDIA_ROOT", default="media")

STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if STORAGE_BACKEND == "s3":
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env("S3_ACCESS_KEY_ID", default=None),
            "secret_key": env("S3_SECRET_ACCESS_KEY", default=None),
            "bucket_name": env("S3_BUCKET_NAME", default=None),
            "endpoint_url": env("S3_ENDPOINT_URL", default=None),
            "region_name": env("S3_REGION", default=None),
            "custom_domain": env("S3_PUBLIC_URL", default=None),
            "querystring_auth": env.bool(
                "S3_USE_PRESIGNED_URLS", default=True
            ),
        },
    }

# ─── CORS et CSRF ─────────────────────────────────────────────────────────────
# CORS et CSRF sont deux mécanismes distincts : CORS autorise les lectures
# cross-origin, CSRF protège les écritures. Aucun wildcard global n'est activé.
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOWED_ORIGIN_REGEXES = env.list(
    "CORS_ALLOWED_ORIGIN_REGEXES", default=[]
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_PATH = env("CSRF_COOKIE_PATH", default="/")
# Vide par défaut (cookie host-only). Aucun domaine global n'est imposé.
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default=None) or None

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None) or None

# ─── Sécurité HTTP ────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.PixeoJWTAuthentication",
        "apps.accounts.authentication.PixeoSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_VERSIONING_CLASS": (
        "rest_framework.versioning.URLPathVersioning"
    ),
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "VERSION_PARAM": "version",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "apps.api.pagination.PixeoPageNumberPagination"
    ),
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.api.exceptions.pixeo_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth_login": env("AUTH_LOGIN_RATE", default="5/min"),
        "auth_refresh": env("AUTH_REFRESH_RATE", default="30/min"),
    },
}

# ─── JWT ──────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("AUTH_ACCESS_TOKEN_LIFETIME_MINUTES", default=10)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("AUTH_REFRESH_TOKEN_LIFETIME_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

AUTH_REFRESH_COOKIE_NAME = env(
    "AUTH_REFRESH_COOKIE_NAME", default="pixeo_refresh"
)
AUTH_REFRESH_COOKIE_SECURE = env.bool(
    "AUTH_REFRESH_COOKIE_SECURE", default=False
)
AUTH_REFRESH_COOKIE_SAMESITE = env(
    "AUTH_REFRESH_COOKIE_SAMESITE", default="Lax"
)
AUTH_REFRESH_COOKIE_PATH = env(
    "AUTH_REFRESH_COOKIE_PATH", default="/api/v1/auth/"
)
# Vide par défaut (cookie host-only). Aucun domaine global n'est imposé ;
# le cookie ne doit pas être partagé avec les sous-domaines tenants.
AUTH_REFRESH_COOKIE_DOMAIN = (
    env("AUTH_REFRESH_COOKIE_DOMAIN", default=None) or None
)

# ─── OpenAPI ──────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Pixeo API",
    "DESCRIPTION": (
        "API REST de Pixeo, versionnée sous `/api/v1/`.\n\n"
        "Les réponses de succès utilisent l'enveloppe "
        "`{\"ok\": true, \"data\": ...}`. Les erreurs utilisent "
        "`{\"ok\": false, \"error\": \"...\", \"code\": \"...\", "
        "\"details\": {...}}` avec un code stable.\n\n"
        "Les propriétés JSON publiques sont en camelCase. La pagination "
        "accepte `page` et `page_size` et renvoie `items`, `total`, `page` "
        "et `pageSize`."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "TAGS": [
        {
            "name": "Technique",
            "description": "Endpoints techniques de la fondation API.",
        },
        {
            "name": "Authentification",
            "description": (
                "Connexion, renouvellement, déconnexion, profil et jeton CSRF."
            ),
        },
    ],
    # La documentation est publique en développement (override dans
    # development.py) et réservée aux administrateurs en production.
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.SessionAuthentication"
    ],
}

# ─── Domaine Pixeo ────────────────────────────────────────────────────────────
PIXEO_BASE_DOMAIN = env("PIXEO_BASE_DOMAIN", default="pixeo.com")
PIXEO_PUBLIC_SCHEME = env("PIXEO_PUBLIC_SCHEME", default="https")
PIXEO_APP_URL = env("PIXEO_APP_URL", default="https://app.pixeo.com")
PIXEO_ADMIN_URL = env("PIXEO_ADMIN_URL", default="https://admin.pixeo.com")
PIXEO_API_URL = env("PIXEO_API_URL", default="https://api.pixeo.com")

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@pixeo.test")

# ─── Cache et Celery ──────────────────────────────────────────────────────────
CACHE_URL = env("CACHE_URL", default="")
if CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pixeo-local",
        }
    }

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="")
CELERY_TASK_ALWAYS_EAGER = env.bool(
    "CELERY_TASK_ALWAYS_EAGER", default=False
)

# ─── Journalisation ───────────────────────────────────────────────────────────
LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "{levelname} {asctime} {name} {process:d} {thread:d} {message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        # Les requêtes SQL contiennent les refresh tokens stockés par
        # SimpleJWT dans OutstandingToken. On ne les journalise jamais, même
        # lorsque le niveau applicatif local est DEBUG.
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "pixeo": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
