"""Vérification CSRF explicite pour les endpoints à cookie.

Les vues DRF sont exemptées de la vérification CSRF par ``APIView.as_view``.
Comme le login crée une session et que refresh/logout utilisent un cookie, ces
endpoints doivent appliquer explicitement ``CsrfViewMiddleware``.
"""

from __future__ import annotations

from rest_framework.authentication import CSRFCheck
from rest_framework.request import Request

from .exceptions import CSRFCheckFailed


def enforce_csrf(request: Request) -> None:
    """Applique les règles CSRF de Django (cookie, en-tête, origine)."""

    check = CSRFCheck(lambda django_request: None)
    django_request = request._request
    check.process_request(django_request)
    reason = check.process_view(django_request, None, (), {})
    if reason:
        raise CSRFCheckFailed()
