"""Tests du health check technique avec contrôle PostgreSQL."""

from __future__ import annotations

import pytest
from django.db import OperationalError
from django.test import Client

pytestmark = pytest.mark.django_db


def test_health_endpoint_reports_database_available():
    response = Client().get("/api/v1/health/", HTTP_HOST="localhost")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "service": "pixeo",
        "database": "available",
    }


def test_health_endpoint_reports_database_unavailable_without_leaking_details(
    monkeypatch,
):
    class BrokenConnection:
        def cursor(self):
            raise OperationalError(
                "secret-db-host:5432 password=should-never-leak"
            )

    monkeypatch.setattr("config.views.connection", BrokenConnection())

    response = Client().get("/api/v1/health/", HTTP_HOST="localhost")

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "service": "pixeo",
        "database": "unavailable",
    }
    body = response.content.decode().lower()
    assert "secret-db-host" not in body
    assert "password" not in body
