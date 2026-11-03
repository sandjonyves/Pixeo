"""Tests de la gestion centralisée des erreurs DRF."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User

pytestmark = [
    pytest.mark.urls("apps.api.tests.test_urls"),
    pytest.mark.django_db,
]


def _authenticated_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
    return client


def _photographer():
    return User.objects.create_user(
        email="photographer@example.com",
        password="StrongPassword123!",
        branding_username="photographer",
    )


def test_validation_error_envelope_is_stable():
    response = APIClient().post(
        "/api/v1/echo/",
        {"firstName": "", "age": 17, "nested": {"postalCode": ""}},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION_ERROR"
    assert payload["error"] == "Les données fournies sont invalides."
    assert payload["details"]["firstName"]
    assert payload["details"]["nested"]["postalCode"]


def test_not_found_does_not_leak_internal_detail():
    response = APIClient().get(
        "/api/v1/not-found/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": "Ressource introuvable.",
        "code": "NOT_FOUND",
        "details": {},
    }
    assert "internal object 42" not in response.content.decode()


def test_method_not_allowed_is_standardized():
    response = APIClient().get(
        "/api/v1/echo/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"
    assert response.json()["details"] == {}


def test_unauthenticated_request_is_401():
    response = APIClient().get(
        "/api/v1/admin-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "Authentification requise.",
        "code": "AUTHENTICATION_REQUIRED",
        "details": {},
    }
    assert response.has_header("WWW-Authenticate")


def test_authenticated_user_without_permission_is_403():
    client = _authenticated_client(_photographer())

    response = client.get(
        "/api/v1/admin-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "error": "Vous n'avez pas les droits nécessaires.",
        "code": "PERMISSION_DENIED",
        "details": {},
    }


def test_rate_limit_preserves_status_and_retry_header():
    response = APIClient().get(
        "/api/v1/throttled/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 429
    assert response.json()["code"] == "RATE_LIMITED"
    assert response["Retry-After"] == "30"


def test_internal_error_is_generic_and_does_not_leak(caplog):
    with caplog.at_level("ERROR", logger="pixeo.api"):
        response = APIClient().get(
            "/api/v1/crash/",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 500
    assert response.json() == {
        "ok": False,
        "error": "Une erreur interne est survenue.",
        "code": "INTERNAL_ERROR",
        "details": {},
    }
    body = response.content.decode().lower()
    assert "super-secret" not in body
    assert "database password" not in body
    assert "traceback" not in body
    assert "super-secret" not in caplog.text
    assert "database password" not in caplog.text
