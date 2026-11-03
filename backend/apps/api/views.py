"""Vues techniques de la fondation API Pixeo."""

from __future__ import annotations

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from .serializers import PixeoRootSerializer


class PixeoAPIRootView(APIRootView):
    """Racine versionnée de l'API, avec enveloppe de succès Pixeo."""

    permission_classes = [AllowAny]
    authentication_classes = []
    schema = AutoSchema()

    @extend_schema(
        tags=["Technique"],
        responses={200: PixeoRootSerializer},
        description=(
            "Racine de la version d'API courante. Les routes métier y seront "
            "découvertes automatiquement lorsqu'elles seront enregistrées."
        ),
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({"ok": True, "data": response.data})
