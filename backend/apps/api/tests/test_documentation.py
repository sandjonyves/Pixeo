"""Tests des endpoints OpenAPI de Pixeo."""

from __future__ import annotations

from django.test import Client


def test_openapi_schema_is_accessible_and_versioned():
    response = Client().get(
        "/api/v1/schema/?format=json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == "Pixeo API"
    assert "camelCase" in schema["info"]["description"]
    assert "/api/v1/" in schema["paths"]
    assert "/api/v1/galleries/" not in schema["paths"]


def test_openapi_documents_auth_endpoints_and_security_schemes():
    response = Client().get(
        "/api/v1/schema/?format=json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    schema = response.json()
    for path in (
        "/api/v1/auth/login/",
        "/api/v1/auth/refresh/",
        "/api/v1/auth/logout/",
        "/api/v1/auth/me/",
        "/api/v1/auth/csrf/",
    ):
        assert path in schema["paths"]

    schemes = schema["components"]["securitySchemes"]
    assert schemes["jwtAuth"]["type"] == "http"
    assert schemes["jwtAuth"]["scheme"] == "bearer"
    assert schemes["cookieAuth"]["type"] == "apiKey"
    assert schemes["cookieAuth"]["in"] == "cookie"

    for path in (
        "/api/v1/auth/login/",
        "/api/v1/auth/refresh/",
        "/api/v1/auth/logout/",
    ):
        parameters = schema["paths"][path]["post"].get("parameters", [])
        assert any(
            parameter["name"] == "X-CSRFToken"
            and parameter["in"] == "header"
            for parameter in parameters
        )


def test_swagger_ui_is_accessible_in_development():
    response = Client().get(
        "/api/v1/docs/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


def test_redoc_is_accessible_in_development():
    response = Client().get(
        "/api/v1/redoc/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert b"redoc" in response.content.lower()
