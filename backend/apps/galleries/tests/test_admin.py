"""Tests de l'administration des galeries Pixeo."""

from __future__ import annotations

import pytest
from django.contrib import admin

from apps.galleries.admin import GalleryAdmin
from apps.galleries.models import Gallery

pytestmark = pytest.mark.django_db


def test_gallery_is_registered_in_admin():
    assert admin.site.is_registered(Gallery)

    model_admin = admin.site._registry[Gallery]
    assert isinstance(model_admin, GalleryAdmin)
    assert model_admin.list_display == (
        "title",
        "photographer",
        "slug",
        "status",
        "created_at",
    )
    assert model_admin.list_filter == ("status",)
    assert model_admin.search_fields == ("title", "slug")
    assert model_admin.readonly_fields == (
        "status",
        "published_at",
        "created_at",
        "updated_at",
    )
