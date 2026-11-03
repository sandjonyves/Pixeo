"""Pagination standard de l'API Pixeo."""

from __future__ import annotations

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PixeoPageNumberPagination(PageNumberPagination):
    """Pagination par numéro de page avec enveloppe Pixeo.

    Le contrat public utilise ``page`` et ``page_size`` en entrée, puis
    ``items``, ``total``, ``page`` et ``pageSize`` en sortie.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        return Response(
            {
                "ok": True,
                "data": {
                    "items": data,
                    "total": self.page.paginator.count,
                    "page": self.page.number,
                    "pageSize": self.get_page_size(self.request) or self.page_size,
                },
            }
        )

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Documente l'enveloppe paginée avec les clés camelCase."""

        return {
            "type": "object",
            "required": ["ok", "data"],
            "properties": {
                "ok": {"type": "boolean", "example": True},
                "data": {
                    "type": "object",
                    "required": ["items", "total", "page", "pageSize"],
                    "properties": {
                        "items": schema,
                        "total": {"type": "integer", "example": 0},
                        "page": {"type": "integer", "example": 1},
                        "pageSize": {"type": "integer", "example": self.page_size},
                    },
                },
            },
        }
