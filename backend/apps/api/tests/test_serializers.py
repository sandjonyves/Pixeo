"""Tests des conventions camelCase des serializers Pixeo."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.api.serializers import (
    PixeoModelSerializer,
    camelize_keys,
    snakeize_keys,
    to_camel_case,
    to_snake_case,
)

pytestmark = pytest.mark.urls("apps.api.tests.test_urls")


def test_identifier_conversion_helpers():
    assert to_camel_case("first_name") == "firstName"
    assert to_camel_case("page_size") == "pageSize"
    assert to_camel_case("firstName") == "firstName"
    assert to_snake_case("firstName") == "first_name"
    assert to_snake_case("pageSize") == "page_size"
    assert to_snake_case("postalCode") == "postal_code"


def test_nested_structure_conversion_is_recursive():
    source = {
        "first_name": "Ada",
        "nested": {"postal_code": "75001"},
        "items": [{"created_at": "2026-11-02T10:00:00Z"}],
    }

    assert camelize_keys(source) == {
        "firstName": "Ada",
        "nested": {"postalCode": "75001"},
        "items": [{"createdAt": "2026-11-02T10:00:00Z"}],
    }
    assert snakeize_keys(camelize_keys(source)) == source


def test_model_serializer_converts_model_field_names():
    class UserSummarySerializer(PixeoModelSerializer):
        class Meta:
            model = User
            fields = ["first_name", "last_name", "created_at"]

    user = User(first_name="Ada", last_name="Lovelace")

    assert UserSummarySerializer(user).data == {
        "firstName": "Ada",
        "lastName": "Lovelace",
        "createdAt": None,
    }


def test_serializer_accepts_and_returns_camel_case():
    client = APIClient()

    response = client.post(
        "/api/v1/echo/",
        {
            "firstName": "Ada",
            "age": 30,
            "nested": {"postalCode": "75001"},
        },
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "data": {
            "firstName": "Ada",
            "age": 30,
            "nested": {"postalCode": "75001"},
        },
    }


def test_validation_errors_use_camel_case_and_keep_details():
    client = APIClient()

    response = client.post(
        "/api/v1/echo/",
        {
            "firstName": "",
            "age": 17,
            "nested": {"postalCode": ""},
        },
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION_ERROR"
    assert set(payload["details"]) == {"firstName", "age", "nested"}
    assert "postalCode" in payload["details"]["nested"]
    assert "first_name" not in payload["details"]
