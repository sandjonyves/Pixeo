"""Gestion centralisée du cookie de refresh token Pixeo."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse


def refresh_cookie_max_age() -> int:
    """Durée de vie du cookie, alignée sur le refresh token."""

    return int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())


def set_refresh_cookie(response: HttpResponse, raw_token: str) -> HttpResponse:
    """Écrit le refresh token dans son cookie HttpOnly."""

    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=refresh_cookie_max_age(),
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )
    return response


def clear_refresh_cookie(response: HttpResponse) -> HttpResponse:
    """Supprime le cookie avec les mêmes attributs de chemin et de domaine.

    ``delete_cookie`` de Django ne reprend pas ``Secure`` dans cette version ;
    on écrit donc explicitement un cookie expiré avec les mêmes attributs.
    """

    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value="",
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )
    return response
