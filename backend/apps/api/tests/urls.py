"""Vues et URLs strictement réservées aux tests de la fondation API.

Aucun endpoint de ce module n'est exposé par la configuration de production.
Ils servent à vérifier réellement les conventions transverses (erreurs,
pagination, permissions et camelCase) sans créer de fausse fonctionnalité
métier.
"""

from __future__ import annotations

from django.urls import path
from rest_framework import serializers
from rest_framework.exceptions import NotFound, Throttled
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import PixeoPageNumberPagination
from apps.api.permissions import IsPhotographer, IsPlatformAdmin
from apps.api.serializers import PixeoSerializer


class NestedEchoSerializer(PixeoSerializer):
    postal_code = serializers.CharField()


class EchoSerializer(PixeoSerializer):
    first_name = serializers.CharField()
    age = serializers.IntegerField(min_value=18)
    nested = NestedEchoSerializer()


class EchoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EchoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"ok": True, "data": serializer.data})


class PhotographerOnlyView(APIView):
    permission_classes = [IsPhotographer]

    def get(self, request, *args, **kwargs):
        return Response({"ok": True, "data": {"scope": "photographer"}})


class AdminOnlyView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request, *args, **kwargs):
        return Response({"ok": True, "data": {"scope": "admin"}})


class NotFoundView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        raise NotFound("internal object 42")


class ThrottledView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        raise Throttled(wait=30)


class CrashView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        raise RuntimeError("database password=super-secret")


class ItemSerializer(PixeoSerializer):
    item_id = serializers.IntegerField()
    display_name = serializers.CharField()


class PaginatedItemsView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ItemSerializer
    pagination_class = PixeoPageNumberPagination

    def get_queryset(self):
        return [
            {"item_id": index, "display_name": f"Item {index}"}
            for index in range(1, 26)
        ]


urlpatterns = [
    path("echo/", EchoView.as_view(), name="test-echo"),
    path(
        "photographer-only/",
        PhotographerOnlyView.as_view(),
        name="test-photographer-only",
    ),
    path("admin-only/", AdminOnlyView.as_view(), name="test-admin-only"),
    path("not-found/", NotFoundView.as_view(), name="test-not-found"),
    path("throttled/", ThrottledView.as_view(), name="test-throttled"),
    path("crash/", CrashView.as_view(), name="test-crash"),
    path("items/", PaginatedItemsView.as_view(), name="test-items"),
]
