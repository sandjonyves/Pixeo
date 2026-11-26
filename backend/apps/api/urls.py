"""Routes versionnées de l'API Pixeo.

Le routeur reçoit les futurs endpoints métier. Les routes d'authentification
sont montées explicitement sous ``/api/<version>/auth/`` pour conserver des
chemins stables et documentés.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.galleries.views import GalleryPhotoViewSet, GalleryViewSet

from .views import PixeoAPIRootView


class PixeoRouter(DefaultRouter):
    """Routeur DRF dont la racine respecte l'enveloppe Pixeo."""

    APIRootView = PixeoAPIRootView
    include_format_suffixes = False


router = PixeoRouter()
router.register("galleries", GalleryViewSet, basename="gallery")

gallery_photo_list = GalleryPhotoViewSet.as_view(
    {"get": "list", "post": "create"}
)
gallery_photo_detail = GalleryPhotoViewSet.as_view(
    {"get": "retrieve", "delete": "destroy"}
)
gallery_photo_reorder = GalleryPhotoViewSet.as_view({"patch": "reorder"})

urlpatterns = [
    path("auth/", include("apps.accounts.auth.urls")),
    *router.urls,
    path(
        "galleries/<uuid:gallery_id>/photos/",
        gallery_photo_list,
        name="gallery-photo-list",
    ),
    path(
        "galleries/<uuid:gallery_id>/photos/order/",
        gallery_photo_reorder,
        name="gallery-photo-order",
    ),
    path(
        "galleries/<uuid:gallery_id>/photos/<uuid:photo_id>/",
        gallery_photo_detail,
        name="gallery-photo-detail",
    ),
]
