"""Routes racine de Pixeo."""

from django.conf import settings
from django.conf.urls.static import static
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

# En développement uniquement, Django sert les fichiers importés depuis
# MEDIA_ROOT. En production, le reverse proxy ou le stockage S3/R2 sert les
# médias ; Django ne doit pas les exposer directement.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
