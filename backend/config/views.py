"""Vues techniques du projet Pixeo."""

from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    """Health check minimal, sans accès base ni information sensible."""
    return JsonResponse({"ok": True, "service": "pixeo"})
