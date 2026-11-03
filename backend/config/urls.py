"""Routes racine de Pixeo."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    # Endpoint historique conservé hors routeur pour préserver exactement son
    # contrat et son comportement Django.
    path("api/v1/health/", health, name="health"),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Routeur versionné : /api/v1/ et futures ressources /api/v1/<resource>/.
    path(
        "api/<version>/",
        include(("apps.api.urls", "api"), namespace="api"),
    ),
]
