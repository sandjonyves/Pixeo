"""Configuration de production Pixeo.

Ce module impose explicitement les secrets, les hôtes, la base PostgreSQL,
les origines CORS/CSRF et les réglages HTTPS. Il ne doit jamais être chargé
avec les valeurs de développement.
"""

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = env.bool("DJANGO_DEBUG", default=False)  # noqa: F405
if DEBUG:
    raise ImproperlyConfigured(
        "DJANGO_DEBUG doit être False en production."
    )

if not SECRET_KEY:  # noqa: F405
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY est obligatoire en production."
    )

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # noqa: F405
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS est obligatoire en production."
    )

DATABASE_URL = env("DATABASE_URL")  # noqa: F405
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=env.int("DATABASE_CONN_MAX_AGE", default=600),  # noqa: F405
    )
}
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    raise ImproperlyConfigured(
        "SQLite n'est pas autorisé en production. Configurez DATABASE_URL "
        "avec PostgreSQL."
    )

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])  # noqa: F405
CORS_ALLOWED_ORIGIN_REGEXES = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGIN_REGEXES",
    default=[r"^https://[a-z0-9-]+\.pixeo\.com$"],
)
if not CORS_ALLOWED_ORIGINS and not CORS_ALLOWED_ORIGIN_REGEXES:
    raise ImproperlyConfigured(
        "Au moins une origine CORS ou une expression régulière CORS est "
        "obligatoire en production."
    )

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405
if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        "CSRF_TRUSTED_ORIGINS est obligatoire en production."
    )

CACHE_URL = env("CACHE_URL")  # noqa: F405
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

SECURE_SSL_REDIRECT = env.bool(  # noqa: F405
    "SECURE_SSL_REDIRECT", default=True
)
SECURE_HSTS_SECONDS = env.int(  # noqa: F405
    "SECURE_HSTS_SECONDS", default=31536000
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(  # noqa: F405
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool(  # noqa: F405
    "SECURE_HSTS_PRELOAD", default=False
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
AUTH_REFRESH_COOKIE_SECURE = True

# Par défaut, les cookies restent host-only (aucun domaine global imposé).
# La stratégie de domaine inter-sous-domaines sera décidée et testée aux lots
# C2/C3 ; elle peut être fournie explicitement par l'environnement.

STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

# La documentation OpenAPI reste réservée aux administrateurs authentifiés
# via la session Django en production.
SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = [  # noqa: F405
    "rest_framework.permissions.IsAdminUser",
]

PIXEO_BASE_DOMAIN = env("PIXEO_BASE_DOMAIN", default="pixeo.com")  # noqa: F405
PIXEO_PUBLIC_SCHEME = env("PIXEO_PUBLIC_SCHEME", default="https")  # noqa: F405
PIXEO_APP_URL = env(  # noqa: F405
    "PIXEO_APP_URL", default="https://app.pixeo.com"
)
PIXEO_ADMIN_URL = env(  # noqa: F405
    "PIXEO_ADMIN_URL", default="https://admin.pixeo.com"
)
PIXEO_API_URL = env(  # noqa: F405
    "PIXEO_API_URL", default="https://api.pixeo.com"
)

LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")  # noqa: F405
LOGGING["root"]["level"] = LOG_LEVEL  # noqa: F405
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL  # noqa: F405
LOGGING["loggers"]["pixeo"]["level"] = LOG_LEVEL  # noqa: F405
