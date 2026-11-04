"""Vérifications de chargement des configurations et des routes techniques."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from django.conf import settings

BACKEND_DIR = Path(__file__).resolve().parents[3]

BASE_ENV = {
    "DJANGO_SECRET_KEY": "test-only-secret-not-used-in-production",
    "DJANGO_DEBUG": "True",
    "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1",
    "DATABASE_URL": "sqlite:///db.sqlite3",
    "CACHE_URL": "",
}

PRODUCTION_ENV = {
    "DJANGO_SECRET_KEY": "test-only-secret-not-used-in-production",
    "DJANGO_DEBUG": "False",
    "DJANGO_ALLOWED_HOSTS": "api.pixeo.com,app.pixeo.com,admin.pixeo.com,.pixeo.com",
    "DJANGO_LOG_LEVEL": "INFO",
    "DATABASE_URL": "postgresql://pixeo:pixeo@localhost:5432/pixeo",
    "CORS_ALLOWED_ORIGINS": "https://app.pixeo.com",
    "CORS_ALLOWED_ORIGIN_REGEXES": r"^https://[a-z0-9-]+\.pixeo\.com$",
    "CSRF_TRUSTED_ORIGINS": "https://app.pixeo.com,https://*.pixeo.com",
    "CACHE_URL": "redis://localhost:6379/0",
    "SECURE_SSL_REDIRECT": "True",
    "SECURE_HSTS_SECONDS": "31536000",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": "True",
    "SECURE_HSTS_PRELOAD": "False",
}


def _run_manage_check(settings_module: str, overrides: dict[str, str]):
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.update(overrides)
    return subprocess.run(
        [
            sys.executable,
            "manage.py",
            "check",
            "--settings",
            settings_module,
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("settings_module", "overrides"),
    [
        ("config.settings.base", {}),
        ("config.settings.development", {"DJANGO_DEBUG": "True"}),
        ("config.settings.production", PRODUCTION_ENV),
    ],
)
def test_settings_modules_load(settings_module, overrides):
    result = _run_manage_check(settings_module, overrides)
    assert result.returncode == 0, result.stdout + result.stderr


def test_development_settings_are_loaded():
    assert settings.SETTINGS_MODULE == "config.settings.development"
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert settings.CORS_ALLOW_ALL_ORIGINS is False
    assert settings.CORS_ALLOW_CREDENTIALS is True
    assert settings.CORS_ALLOWED_ORIGINS
    assert settings.CORS_ALLOWED_ORIGIN_REGEXES
    assert settings.CSRF_TRUSTED_ORIGINS


def test_auth_settings_are_centralized_and_secure():
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=10)
    assert settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] == timedelta(days=7)
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True
    assert settings.AUTH_REFRESH_COOKIE_NAME == "pixeo_refresh"
    assert settings.AUTH_REFRESH_COOKIE_PATH == "/api/v1/auth/"
    assert settings.AUTH_REFRESH_COOKIE_SAMESITE == "Lax"
    assert settings.AUTH_REFRESH_COOKIE_DOMAIN is None
    assert settings.AUTH_REFRESH_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_HTTPONLY is False
    assert settings.CSRF_COOKIE_SAMESITE == "Lax"
    assert settings.CSRF_COOKIE_DOMAIN is None
    assert settings.CORS_ALLOW_ALL_ORIGINS is False
    assert settings.CORS_ALLOW_CREDENTIALS is True
    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] == {
        "auth_login": "5/min",
        "auth_refresh": "30/min",
    }


def test_development_settings_enable_debug_when_requested():
    # pytest-django force DEBUG=False dans le processus de test. On vérifie donc
    # le chargement réel du module de développement dans un sous-processus isolé.
    env = os.environ.copy()
    env.update(BASE_ENV)
    env["DJANGO_DEBUG"] = "True"
    code = (
        "import os, django; "
        "os.environ['DJANGO_SETTINGS_MODULE']="
        "'config.settings.development'; "
        "django.setup(); "
        "from django.conf import settings; "
        "print(settings.DEBUG)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "True"
