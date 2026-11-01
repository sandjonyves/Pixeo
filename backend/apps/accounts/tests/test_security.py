"""Tests de sécurité de la configuration et absence de secrets en dur."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from django.conf import settings

from apps.accounts.tests.test_settings import PRODUCTION_ENV

BACKEND_DIR = Path(__file__).resolve().parents[3]
SECRET_PATTERN = re.compile(
    r"(SECRET_KEY|PASSWORD|ACCESS_KEY|SECRET_ACCESS_KEY|PRIVATE_KEY)"
    r"\s*=\s*['\"][^'\"]+['\"]"
)

PROBE = """
import json
import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = %r
django.setup()

from django.conf import settings

print(json.dumps({
    "DEBUG": settings.DEBUG,
    "SECURE_SSL_REDIRECT": settings.SECURE_SSL_REDIRECT,
    "SESSION_COOKIE_SECURE": settings.SESSION_COOKIE_SECURE,
    "CSRF_COOKIE_SECURE": settings.CSRF_COOKIE_SECURE,
    "AUTH_REFRESH_COOKIE_SECURE": settings.AUTH_REFRESH_COOKIE_SECURE,
    "CORS_ALLOW_ALL_ORIGINS": settings.CORS_ALLOW_ALL_ORIGINS,
    "CORS_ALLOWED_ORIGINS": settings.CORS_ALLOWED_ORIGINS,
    "CORS_ALLOWED_ORIGIN_REGEXES": settings.CORS_ALLOWED_ORIGIN_REGEXES,
    "CSRF_TRUSTED_ORIGINS": settings.CSRF_TRUSTED_ORIGINS,
    "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    "DB_ENGINE": settings.DATABASES["default"]["ENGINE"],
    "CSRF_COOKIE_DOMAIN": settings.CSRF_COOKIE_DOMAIN,
    "SESSION_COOKIE_DOMAIN": settings.SESSION_COOKIE_DOMAIN,
    "AUTH_REFRESH_COOKIE_DOMAIN": settings.AUTH_REFRESH_COOKIE_DOMAIN,
    "SECURE_HSTS_SECONDS": settings.SECURE_HSTS_SECONDS,
    "SECURE_PROXY_SSL_HEADER": settings.SECURE_PROXY_SSL_HEADER,
}))
"""


def _probe_production_settings() -> dict:
    env = os.environ.copy()
    env.update(PRODUCTION_ENV)
    result = subprocess.run(
        [sys.executable, "-c", PROBE % "config.settings.production"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def _run_production_check(overrides: dict[str, str]):
    env = os.environ.copy()
    env.update(PRODUCTION_ENV)
    env.update(overrides)
    return subprocess.run(
        [
            sys.executable,
            "manage.py",
            "check",
            "--settings",
            "config.settings.production",
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_no_hardcoded_secrets_in_backend_code():
    paths = list((BACKEND_DIR / "config").rglob("*.py"))
    paths += list((BACKEND_DIR / "apps").rglob("*.py"))

    for path in paths:
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert not SECRET_PATTERN.search(text), (
            f"Valeur potentiellement secrète codée en dur dans {path}"
        )


def test_development_security_settings():
    assert settings.CORS_ALLOW_ALL_ORIGINS is False
    assert settings.CORS_ALLOW_CREDENTIALS is True
    assert settings.CSRF_COOKIE_DOMAIN is None
    assert settings.SESSION_COOKIE_DOMAIN is None
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert (
        settings.PASSWORD_HASHERS[0]
        == "django.contrib.auth.hashers.Argon2PasswordHasher"
    )


def test_production_settings_are_hardened():
    probe = _probe_production_settings()

    assert probe["DEBUG"] is False
    assert probe["SECURE_SSL_REDIRECT"] is True
    assert probe["SESSION_COOKIE_SECURE"] is True
    assert probe["CSRF_COOKIE_SECURE"] is True
    assert probe["AUTH_REFRESH_COOKIE_SECURE"] is True
    assert probe["CORS_ALLOW_ALL_ORIGINS"] is False
    assert "https://app.pixeo.com" in probe["CORS_ALLOWED_ORIGINS"]
    assert probe["CORS_ALLOWED_ORIGIN_REGEXES"]
    assert "https://app.pixeo.com" in probe["CSRF_TRUSTED_ORIGINS"]
    assert probe["DB_ENGINE"] == "django.db.backends.postgresql"
    assert probe["CSRF_COOKIE_DOMAIN"] is None
    assert probe["SESSION_COOKIE_DOMAIN"] is None
    assert probe["AUTH_REFRESH_COOKIE_DOMAIN"] is None
    assert probe["SECURE_HSTS_SECONDS"] > 0
    assert probe["SECURE_PROXY_SSL_HEADER"] == [
        "HTTP_X_FORWARDED_PROTO",
        "https",
    ]
    assert "api.pixeo.com" in probe["ALLOWED_HOSTS"]


def test_production_rejects_debug_true():
    result = _run_production_check({"DJANGO_DEBUG": "True"})
    assert result.returncode != 0
    assert "DJANGO_DEBUG" in result.stdout + result.stderr


def test_production_rejects_sqlite():
    result = _run_production_check(
        {"DATABASE_URL": "sqlite:///db.sqlite3"}
    )
    assert result.returncode != 0
    assert "SQLite" in result.stdout + result.stderr


def test_production_requires_secret_key():
    result = _run_production_check({"DJANGO_SECRET_KEY": ""})
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stdout + result.stderr


def test_production_requires_allowed_hosts():
    result = _run_production_check({"DJANGO_ALLOWED_HOSTS": ""})
    assert result.returncode != 0
    assert "DJANGO_ALLOWED_HOSTS" in result.stdout + result.stderr
