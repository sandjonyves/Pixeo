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
