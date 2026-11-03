"""Tests de la configuration transversale de l'API."""

from __future__ import annotations

from django.conf import settings


def test_api_foundation_settings():
    rest_framework = settings.REST_FRAMEWORK

    assert rest_framework["DEFAULT_VERSION"] == "v1"
    assert rest_framework["ALLOWED_VERSIONS"] == ["v1"]
    assert rest_framework["VERSION_PARAM"] == "version"
    assert rest_framework["PAGE_SIZE"] == 20
    assert rest_framework["DEFAULT_PAGINATION_CLASS"] == (
        "apps.api.pagination.PixeoPageNumberPagination"
    )
    assert rest_framework["EXCEPTION_HANDLER"] == (
        "apps.api.exceptions.pixeo_exception_handler"
    )
    assert rest_framework["DEFAULT_PERMISSION_CLASSES"] == [
        "rest_framework.permissions.IsAuthenticated",
    ]


def test_documentation_is_public_in_development():
    assert settings.SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] == [
        "rest_framework.permissions.AllowAny",
    ]
