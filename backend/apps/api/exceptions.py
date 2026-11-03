"""Gestion centralisée des erreurs de l'API Pixeo.

Toutes les erreurs DRF sont transformées en enveloppe stable :

``{"ok": false, "error": "...", "code": "...", "details": {}}``

Les exceptions non gérées sont journalisées côté serveur et transformées en
HTTP 500 générique : aucun message, secret ou trace Python n'est renvoyé.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .serializers import camelize_keys

logger = logging.getLogger("pixeo.api")

_ERRORS_BY_STATUS = {
    status.HTTP_400_BAD_REQUEST: (
        "INVALID_REQUEST",
        "La requête est invalide.",
    ),
    status.HTTP_401_UNAUTHORIZED: (
        "AUTHENTICATION_REQUIRED",
        "Authentification requise.",
    ),
    status.HTTP_403_FORBIDDEN: (
        "PERMISSION_DENIED",
        "Vous n'avez pas les droits nécessaires.",
    ),
    status.HTTP_404_NOT_FOUND: (
        "NOT_FOUND",
        "Ressource introuvable.",
    ),
    status.HTTP_405_METHOD_NOT_ALLOWED: (
        "METHOD_NOT_ALLOWED",
        "Méthode HTTP non autorisée.",
    ),
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: (
        "UNSUPPORTED_MEDIA_TYPE",
        "Type de contenu non pris en charge.",
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: (
        "RATE_LIMITED",
        "Trop de requêtes. Réessayez plus tard.",
    ),
}


def _validation_details(response: Response) -> Any:
    """Préserve les détails de validation en les passant en camelCase."""

    details = camelize_keys(response.data)
    if isinstance(details, dict):
        return details
    return {"nonFieldErrors": details}


def _error_payload(exc: Exception, response: Response) -> dict[str, Any]:
    if isinstance(exc, exceptions.ValidationError):
        return {
            "ok": False,
            "error": "Les données fournies sont invalides.",
            "code": "VALIDATION_ERROR",
            "details": _validation_details(response),
        }

    if isinstance(exc, exceptions.NotAuthenticated):
        code, message = (
            "AUTHENTICATION_REQUIRED",
            "Authentification requise.",
        )
    elif isinstance(exc, exceptions.AuthenticationFailed):
        code, message = (
            "AUTHENTICATION_FAILED",
            "Identifiants invalides.",
        )
    elif isinstance(
        exc,
        (exceptions.PermissionDenied, DjangoPermissionDenied),
    ):
        code, message = (
            "PERMISSION_DENIED",
            "Vous n'avez pas les droits nécessaires.",
        )
    elif isinstance(exc, (exceptions.NotFound, Http404)):
        code, message = ("NOT_FOUND", "Ressource introuvable.")
    elif isinstance(exc, exceptions.MethodNotAllowed):
        code, message = (
            "METHOD_NOT_ALLOWED",
            "Méthode HTTP non autorisée.",
        )
    elif isinstance(exc, exceptions.Throttled):
        code, message = (
            "RATE_LIMITED",
            "Trop de requêtes. Réessayez plus tard.",
        )
    elif isinstance(exc, exceptions.ParseError):
        code, message = ("INVALID_REQUEST", "La requête est invalide.")
    else:
        code, message = _ERRORS_BY_STATUS.get(
            response.status_code,
            ("API_ERROR", "La requête n'a pas pu être traitée."),
        )

    return {
        "ok": False,
        "error": message,
        "code": code,
        "details": {},
    }


def pixeo_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Point d'entrée DRF pour toutes les erreurs de l'API."""

    response = drf_exception_handler(exc, context)

    if response is None:
        request = context.get("request")
        logger.error(
            "Unhandled API exception (%s) on %s",
            exc.__class__.__name__,
            getattr(request, "path", "unknown"),
        )
        return Response(
            {
                "ok": False,
                "error": "Une erreur interne est survenue.",
                "code": "INTERNAL_ERROR",
                "details": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response.data = _error_payload(exc, response)
    return response
