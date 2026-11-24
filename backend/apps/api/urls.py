"""Routes versionnées de l'API Pixeo.

Le routeur reçoit les futurs endpoints métier. Les routes d'authentification
sont montées explicitement sous ``/api/<version>/auth/`` pour conserver des
chemins stables et documentés.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.galleries.views import GalleryViewSet

from .views import PixeoAPIRootView


class PixeoRouter(DefaultRouter):
    """Routeur DRF dont la racine respecte l'enveloppe Pixeo."""

    APIRootView = PixeoAPIRootView
    include_format_suffixes = False


router = PixeoRouter()
router.register("galleries", GalleryViewSet, basename="gallery")

urlpatterns = [
    path("auth/", include("apps.accounts.auth.urls")),
    *router.urls,
]
