"""Configuration locale de développement Pixeo."""

from .base import *  # noqa: F401,F403

DEBUG = env.bool("DJANGO_DEBUG", default=True)  # noqa: F405

ALLOWED_HOSTS = env.list(  # noqa: F405
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", ".lvh.me", ".pixeo.localhost"],
)

# Origines frontend autorisées explicitement en développement.
CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://app.lvh.me:3000",
        "http://admin.lvh.me:3000",
        "http://yves.lvh.me:3000",
    ],
)
CORS_ALLOWED_ORIGIN_REGEXES = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGIN_REGEXES",
    default=[r"^http://[a-z0-9-]+\.lvh\.me:3000$"],
)

CSRF_TRUSTED_ORIGINS = env.list(  # noqa: F405
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://app.lvh.me:3000",
        "http://admin.lvh.me:3000",
        "http://api.lvh.me:8000",
        "http://*.lvh.me:3000",
    ],
)

PIXEO_BASE_DOMAIN = env("PIXEO_BASE_DOMAIN", default="lvh.me")  # noqa: F405
PIXEO_PUBLIC_SCHEME = env("PIXEO_PUBLIC_SCHEME", default="http")  # noqa: F405
PIXEO_APP_URL = env(  # noqa: F405
    "PIXEO_APP_URL", default="http://app.lvh.me:3000"
)
PIXEO_ADMIN_URL = env(  # noqa: F405
    "PIXEO_ADMIN_URL", default="http://admin.lvh.me:3000"
)
PIXEO_API_URL = env(  # noqa: F405
    "PIXEO_API_URL", default="http://api.lvh.me:8000"
)

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
AUTH_REFRESH_COOKIE_SECURE = False

LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="DEBUG")  # noqa: F405
LOGGING["root"]["level"] = LOG_LEVEL  # noqa: F405
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL  # noqa: F405
LOGGING["loggers"]["pixeo"]["level"] = LOG_LEVEL  # noqa: F405

# La documentation OpenAPI est librement consultable en développement.
SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = [  # noqa: F405
    "rest_framework.permissions.AllowAny",
]
