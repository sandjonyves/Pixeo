"""Utilitaires communs aux tests d'authentification."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from rest_framework.test import APIClient

LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
ME_URL = "/api/v1/auth/me/"
CSRF_URL = "/api/v1/auth/csrf/"

PASSWORD = "StrongPassword123!"


def login(
    client: APIClient,
    email: str,
    password: str = PASSWORD,
    **extra: Any,
):
    if "HTTP_X_CSRFTOKEN" not in extra:
        extra["HTTP_X_CSRFTOKEN"] = get_csrf(client)
    return client.post(
        LOGIN_URL,
        {"email": email, "password": password},
        format="json",
        **extra,
    )


def get_csrf(client: APIClient) -> str:
    response = client.get(CSRF_URL)
    assert response.status_code == 200
    return response.json()["data"]["csrfToken"]


def refresh(client: APIClient, csrf_token: str, **extra: Any):
    return client.post(
        REFRESH_URL,
        HTTP_X_CSRFTOKEN=csrf_token,
        **extra,
    )


def logout(client: APIClient, csrf_token: str, **extra: Any):
    return client.post(
        LOGOUT_URL,
        HTTP_X_CSRFTOKEN=csrf_token,
        **extra,
    )


def me(client: APIClient, access_token: str, **extra: Any):
    return client.get(
        ME_URL,
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
        **extra,
    )


def refresh_cookie(response, name: str | None = None):
    cookie_name = name or settings.AUTH_REFRESH_COOKIE_NAME
    return response.cookies.get(cookie_name)


def refresh_cookie_value(response, name: str | None = None) -> str:
    cookie = refresh_cookie(response, name)
    assert cookie is not None
    return cookie.value
