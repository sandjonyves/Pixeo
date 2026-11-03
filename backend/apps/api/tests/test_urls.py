"""Racine URL de test, limitée aux endpoints de test de l'API."""

from django.urls import include, path

urlpatterns = [
    path("api/<version>/", include("apps.api.tests.urls")),
]
