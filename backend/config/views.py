"""Vues techniques du projet Pixeo."""

import logging

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger("pixeo.health")


@require_GET
def health(request):
    """Health check technique avec vérification réelle de la base.

    La réponse ne contient jamais les identifiants de connexion ni le détail
    des exceptions. Un échec base renvoie HTTP 503.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # noqa: BLE001 - health check volontairement large
        logger.warning(
            "Database health check failed (%s).", exc.__class__.__name__
        )
        return JsonResponse(
            {
                "ok": False,
                "service": "pixeo",
                "database": "unavailable",
            },
            status=503,
        )

    return JsonResponse(
        {
            "ok": True,
            "service": "pixeo",
            "database": "available",
        }
    )
