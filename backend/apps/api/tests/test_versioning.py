"""Tests du versionnement URL de l'API Pixeo."""

from __future__ import annotations

import pytest
from django.test import Client
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db


def test_health_route_remains_available_at_v1():
    assert reverse("health") == "/api/v1/health/"

    response = Client().get("/api/v1/health/", HTTP_HOST="localhost")

    assert response.status_code == 200
    assert response.json()["database"] == "available"


def test_api_root_is_versioned_and_uses_success_envelope():
    assert reverse("api:api-root", kwargs={"version": "v1"}) == "/api/v1/"

    response = Client().get("/api/v1/", HTTP_HOST="localhost")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": {}}


def test_unsupported_api_version_is_rejected():
    response = Client().get("/api/v2/", HTTP_HOST="localhost")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
