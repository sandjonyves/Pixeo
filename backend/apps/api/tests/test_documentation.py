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
    assert "/api/v1/galleries/" in schema["paths"]
    assert "/api/v1/galleries/{id}/" in schema["paths"]


def test_openapi_documents_auth_endpoints_and_security_schemes():
    response = Client().get(
        "/api/v1/schema/?format=json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    schema = response.json()
    for path in (
        "/api/v1/auth/register/",
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

    register_operation = schema["paths"]["/api/v1/auth/register/"]["post"]
    assert "201" in register_operation["responses"]
    register_parameters = register_operation.get("parameters", [])
    assert not any(
        parameter["name"] == "X-CSRFToken"
        for parameter in register_parameters
    )

    request_ref = register_operation["requestBody"]["content"][
        "application/json"
    ]["schema"]["$ref"].rsplit("/", 1)[-1]
    request_schema = schema["components"]["schemas"][request_ref]
    assert set(request_schema["properties"]) == {
        "email",
        "password",
        "passwordConfirmation",
        "brandingUsername",
    }
    assert set(request_schema["required"]) == {
        "email",
        "password",
        "passwordConfirmation",
        "brandingUsername",
    }


def test_openapi_documents_gallery_endpoints():
    response = Client().get(
        "/api/v1/schema/?format=json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    schema = response.json()

    list_operation = schema["paths"]["/api/v1/galleries/"]["get"]
    create_operation = schema["paths"]["/api/v1/galleries/"]["post"]
    detail_operations = schema["paths"]["/api/v1/galleries/{id}/"]
    assert set(detail_operations) >= {"get", "patch", "delete"}

    assert "Galeries" in list_operation["tags"]
    assert "status" in {
        parameter["name"]
        for parameter in list_operation.get("parameters", [])
    }
    assert list_operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("PaginatedGallerySchemaList")

    request_ref = create_operation["requestBody"]["content"][
        "application/json"
    ]["schema"]["$ref"].rsplit("/", 1)[-1]
    request_schema = schema["components"]["schemas"][request_ref]
    assert set(request_schema["properties"]) == {
        "title",
        "slug",
        "description",
    }
    assert set(request_schema["required"]) == {"title", "slug"}
    assert "photographer" not in request_schema["properties"]
    assert "status" not in request_schema["properties"]
    assert "publishedAt" not in request_schema["properties"]

    patch_operation = detail_operations["patch"]
    patch_ref = patch_operation["requestBody"]["content"]["application/json"][
        "schema"
    ]["$ref"].rsplit("/", 1)[-1]
    patch_schema = schema["components"]["schemas"][patch_ref]
    assert set(patch_schema["properties"]) == {
        "title",
        "slug",
        "description",
    }
    assert "required" not in patch_schema

    response_ref = create_operation["responses"]["201"]["content"][
        "application/json"
    ]["schema"]["$ref"].rsplit("/", 1)[-1]
    response_schema = schema["components"]["schemas"][response_ref]
    data_ref = response_schema["properties"]["data"]["$ref"].rsplit("/", 1)[-1]
    gallery_schema = schema["components"]["schemas"][data_ref]
    assert set(gallery_schema["properties"]) == {
        "id",
        "title",
        "slug",
        "description",
        "status",
        "publishedAt",
        "createdAt",
        "updatedAt",
    }
    assert "204" in detail_operations["delete"]["responses"]


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
