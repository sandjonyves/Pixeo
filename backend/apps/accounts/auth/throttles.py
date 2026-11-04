"""Throttling des tentatives de connexion et de renouvellement."""

from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle


class AuthLoginThrottle(SimpleRateThrottle):
    """Limite les tentatives de connexion par adresse IP."""

    scope = "auth_login"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class AuthRefreshThrottle(SimpleRateThrottle):
    """Limite les renouvellements de session par adresse IP."""

    scope = "auth_refresh"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
