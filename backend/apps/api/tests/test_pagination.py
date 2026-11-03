"""Tests de la pagination standard Pixeo."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.api.pagination import PixeoPageNumberPagination

pytestmark = pytest.mark.urls("apps.api.tests.test_urls")


def _get_items(**params):
    response = APIClient().get(
        "/api/v1/items/",
        params,
        HTTP_HOST="localhost",
    )
    return response


def test_default_page_size_is_twenty():
    response = _get_items()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["total"] == 25
    assert payload["data"]["page"] == 1
    assert payload["data"]["pageSize"] == 20
    assert len(payload["data"]["items"]) == 20
    assert payload["data"]["items"][0] == {
        "itemId": 1,
        "displayName": "Item 1",
    }


def test_page_and_page_size_query_parameters():
    response = _get_items(page=2, page_size=10)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["page"] == 2
    assert payload["pageSize"] == 10
    assert payload["total"] == 25
    assert len(payload["items"]) == 10
    assert payload["items"][0]["itemId"] == 11


def test_page_size_is_capped_at_one_hundred():
    response = _get_items(page_size=101)

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["pageSize"] == 100
    assert payload["total"] == 25
    assert len(payload["items"]) == 25


def test_invalid_page_uses_standard_error_envelope():
    response = _get_items(page=999)

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": "Ressource introuvable.",
        "code": "NOT_FOUND",
        "details": {},
    }


def test_pagination_schema_uses_camel_case():
    schema = PixeoPageNumberPagination().get_paginated_response_schema(
        {"type": "array"}
    )

    data_schema = schema["properties"]["data"]["properties"]
    assert "pageSize" in data_schema
    assert "page_size" not in data_schema
