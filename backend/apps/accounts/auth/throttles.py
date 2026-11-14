"""Throttling des tentatives de connexion et de renouvellement.

DRF utilise ``X-Forwarded-For`` dès que ``NUM_PROXIES`` est renseigné, et même
lorsqu'il vaut ``None``. Comme la topologie du reverse proxy n'est pas garantie
par le dépôt, les throttles Pixeo n'utilisent pas ``get_ident()`` de DRF : par
défaut, seule l'adresse de la connexion TCP (``REMOTE_ADDR``) fait foi.

``AUTH_TRUSTED_PROXY_COUNT`` permet d'activer explicitement la lecture de
``X-Forwarded-For`` après vérification de la topologie. La valeur représente le
nombre exact de proxys de confiance qui ajoutent chacun une entrée à l'en-tête.
Elle doit rester à ``0`` tant que ce nombre n'a pas été vérifié.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


def get_client_ident(request) -> str:
    """Retourne l'identité réseau utilisée pour le throttling.

    Sans proxy de confiance configuré, ``X-Forwarded-For`` est ignoré : un
    client ne peut donc pas changer d'identité en forgeant cet en-tête. Lorsque
    des proxys de confiance sont explicitement déclarés, l'adresse client est
    lue à la position attendue en partant de la droite de l'en-tête.
    """

    remote_addr = request.META.get("REMOTE_ADDR") or ""
    try:
        trusted_proxy_count = int(
            getattr(settings, "AUTH_TRUSTED_PROXY_COUNT", 0)
        )
    except (TypeError, ValueError):
        trusted_proxy_count = 0

    if trusted_proxy_count <= 0:
        return remote_addr

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") or ""
    addresses = [
        address.strip()
        for address in forwarded_for.split(",")
        if address.strip()
    ]
    if len(addresses) < trusted_proxy_count:
        # Topologie incohérente : ne pas interpréter une valeur incomplète.
        return remote_addr

    return addresses[-trusted_proxy_count]


class PixeoAuthThrottle(SimpleRateThrottle):
    """Base commune aux throttles d'authentification Pixeo."""

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": get_client_ident(request),
        }


class AuthLoginThrottle(PixeoAuthThrottle):
    """Limite les tentatives de connexion par identité réseau."""

    scope = "auth_login"


class AuthRefreshThrottle(PixeoAuthThrottle):
    """Limite les renouvellements de session par identité réseau."""

    scope = "auth_refresh"


class AuthRegisterThrottle(PixeoAuthThrottle):
    """Limite les créations de compte par identité réseau."""

    scope = "auth_register"
