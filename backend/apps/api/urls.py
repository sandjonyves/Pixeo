"""Routes versionnées de l'API Pixeo.

Le routeur est volontairement vide en A4 : les endpoints métier seront
enregistrés dans les lots suivants, sans modifier le préfixe public
``/api/<version>/``.
"""

from rest_framework.routers import DefaultRouter

from .views import PixeoAPIRootView


class PixeoRouter(DefaultRouter):
    """Routeur DRF dont la racine respecte l'enveloppe Pixeo."""

    APIRootView = PixeoAPIRootView
    include_format_suffixes = False


router = PixeoRouter()

# Les futurs ViewSets seront enregistrés ici :
# router.register("galleries", GalleryViewSet, basename="gallery")

urlpatterns = router.urls
