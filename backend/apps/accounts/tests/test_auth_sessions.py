"""Tests du renouvellement et de la déconnexion des sessions Pixeo."""

from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.tests.auth_helpers import (
    LOGOUT_URL,
    REFRESH_URL,
    get_csrf,
    login,
    logout,
    refresh,
    refresh_cookie,
    refresh_cookie_value,
)

import pytest

pytestmark = pytest.mark.django_db


def _set_refresh_cookie(client, value: str) -> None:
    client.cookies[settings.AUTH_REFRESH_COOKIE_NAME] = value


def test_refresh_rotates_token_and_blacklists_old_one(
    api_client, photographer
):
    login_response = login(api_client, photographer.email)
    old_refresh = refresh_cookie_value(login_response)
    csrf_token = get_csrf(api_client)

    response = refresh(api_client, csrf_token)

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["accessToken"]
    assert "refresh" not in payload["data"]
    assert "refreshToken" not in payload["data"]

    new_refresh = refresh_cookie_value(response)
    assert new_refresh != old_refresh
    assert BlacklistedToken.objects.count() == 1
    assert OutstandingToken.objects.filter(user=photographer).count() == 2

    # L'ancien refresh token ne peut plus être réutilisé.
    _set_refresh_cookie(api_client, old_refresh)
    reuse = refresh(api_client, csrf_token)
    assert reuse.status_code == 401
    assert reuse.json()["code"] == "TOKEN_REVOKED"
    assert refresh_cookie(reuse) is not None
    assert int(refresh_cookie(reuse)["max-age"]) == 0

    # Politique A5 : SimpleJWT blackliste le jeton rejoué, pas sa famille.
    # R2 reste donc utilisable après la détection du rejeu de R1.
    _set_refresh_cookie(api_client, new_refresh)
    after_replay = refresh(api_client, csrf_token)
    assert after_replay.status_code == 200
    assert after_replay.json()["data"]["accessToken"]
    assert refresh_cookie_value(after_replay) != new_refresh


def test_refresh_without_csrf_is_refused(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    response = api_client.post(REFRESH_URL)

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert refresh_cookie(response) is None

    # La session reste utilisable après un échec CSRF, avec le bon jeton.
    retry = refresh(api_client, csrf_token)
    assert retry.status_code == 200


def test_refresh_with_invalid_csrf_is_refused(api_client, photographer):
    login(api_client, photographer.email)
    get_csrf(api_client)

    response = api_client.post(REFRESH_URL, HTTP_X_CSRFTOKEN="invalid-token")

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"


def test_refresh_without_cookie_returns_token_invalid_and_clears_cookie(
    api_client,
):
    csrf_token = get_csrf(api_client)

    response = refresh(api_client, csrf_token)

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALID"
    cookie = refresh_cookie(response)
    assert cookie is not None
    assert int(cookie["max-age"]) == 0


def test_refresh_with_invalid_token_returns_token_invalid(
    api_client, photographer
):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)
    _set_refresh_cookie(api_client, "not-a-valid-jwt")

    response = refresh(api_client, csrf_token)

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALID"
    assert int(refresh_cookie(response)["max-age"]) == 0


def test_refresh_with_expired_token_returns_token_expired(
    api_client, photographer
):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    expired = RefreshToken.for_user(photographer)
    expired.set_exp(
        from_time=timezone.now() - expired.lifetime - timedelta(days=1)
    )
    _set_refresh_cookie(api_client, str(expired))

    response = refresh(api_client, csrf_token)

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_EXPIRED"
    assert int(refresh_cookie(response)["max-age"]) == 0


def test_suspended_account_cannot_refresh(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    photographer.is_suspended = True
    photographer.save(update_fields=["is_suspended"])

    response = refresh(api_client, csrf_token)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"
    assert int(refresh_cookie(response)["max-age"]) == 0
    assert BlacklistedToken.objects.count() == 0


def test_disabled_account_cannot_refresh(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    photographer.is_active = False
    photographer.save(update_fields=["is_active"])

    response = refresh(api_client, csrf_token)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_DISABLED"
    assert int(refresh_cookie(response)["max-age"]) == 0
    assert BlacklistedToken.objects.count() == 0


def test_logout_blacklists_refresh_token_and_clears_cookie(
    api_client, photographer
):
    login_response = login(api_client, photographer.email)
    old_refresh = refresh_cookie_value(login_response)
    csrf_token = get_csrf(api_client)

    response = logout(api_client, csrf_token)

    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": {"loggedOut": True}}
    cookie = refresh_cookie(response)
    assert cookie is not None
    assert int(cookie["max-age"]) == 0
    assert BlacklistedToken.objects.count() == 1

    _set_refresh_cookie(api_client, old_refresh)
    retry = refresh(api_client, csrf_token)
    assert retry.status_code == 401
    assert retry.json()["code"] == "TOKEN_REVOKED"


def test_logout_without_cookie_is_idempotent(api_client):
    csrf_token = get_csrf(api_client)

    response = logout(api_client, csrf_token)

    assert response.status_code == 200
    assert response.json()["data"]["loggedOut"] is True
    assert int(refresh_cookie(response)["max-age"]) == 0


def test_logout_without_csrf_is_refused(api_client, photographer):
    login(api_client, photographer.email)
    get_csrf(api_client)

    response = api_client.post(LOGOUT_URL)

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert refresh_cookie(response) is None


def test_logout_with_invalid_cookie_still_succeeds(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)
    _set_refresh_cookie(api_client, "invalid-token")

    response = logout(api_client, csrf_token)

    assert response.status_code == 200
    assert int(refresh_cookie(response)["max-age"]) == 0


def test_logout_does_not_return_token_details(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    response = logout(api_client, csrf_token)

    body = response.content.decode().lower()
    assert "token" not in body
    assert "password" not in body
    assert "invalid-token" not in body


def test_auth_flow_does_not_log_tokens(api_client, photographer):
    records: list[str] = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = CaptureHandler()
    loggers = [
        logging.getLogger("django.db.backends"),
        logging.getLogger("django.request"),
        logging.getLogger("pixeo"),
    ]
    for logger in loggers:
        logger.addHandler(handler)

    try:
        login_response = login(api_client, photographer.email)
        access_token = login_response.json()["data"]["accessToken"]
        first_refresh = refresh_cookie_value(login_response)

        csrf_token = get_csrf(api_client)
        refresh_response = refresh(api_client, csrf_token)
        second_refresh = refresh_cookie_value(refresh_response)

        logout(api_client, csrf_token)
    finally:
        for logger in loggers:
            logger.removeHandler(handler)

    logs = "\n".join(records)
    assert first_refresh not in logs
    assert second_refresh not in logs
    assert access_token not in logs
