"""Service transactionnel d'inscription Pixeo.

La création du compte, de l'abonnement Free et des paramètres de studio est
réalisée dans une seule transaction. Une erreur sur l'une des étapes annule
l'ensemble : aucun compte partiel ne doit rester en base.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.auth.exceptions import (
    RegistrationConflict,
    RegistrationUnavailable,
)
from apps.accounts.models import User, UserRole
from apps.billing.models import Plan, Subscription, SubscriptionStatus
from apps.studios.models import BrandingSettings, HomepageSettings

FREE_PLAN_CODE = "free"


def get_free_plan() -> Plan:
    """Retourne le plan Free actif, verrouillé pour la transaction courante.

    Le verrou de ligne empêche qu'une désactivation concurrente du plan permette
    de créer un abonnement vers un plan devenu inactif. La fonction doit être
    appelée à l'intérieur de ``transaction.atomic()``.
    """

    try:
        return Plan.objects.select_for_update().get(
            code=FREE_PLAN_CODE,
            is_active=True,
        )
    except Plan.DoesNotExist as exc:
        raise RegistrationUnavailable() from exc


def register_photographer(
    *,
    email: str,
    password: str,
    branding_username: str,
) -> User:
    """Crée un photographe et initialise son espace Pixeo.

    Le rôle est imposé côté serveur. Le mot de passe est hashé par le manager
    Django et n'est jamais journalisé ni retourné.
    """

    normalized_email = (email or "").strip().lower()
    normalized_branding = (branding_username or "").strip().lower()

    try:
        with transaction.atomic():
            free_plan = get_free_plan()
            user = User.objects.create_user(
                email=normalized_email,
                password=password,
                branding_username=normalized_branding,
                role=UserRole.PHOTOGRAPHER,
                is_staff=False,
                is_superuser=False,
                is_active=True,
                is_suspended=False,
            )

            Subscription.objects.create(
                user=user,
                plan=free_plan,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=timezone.now(),
                current_period_end=None,
                cancel_at_period_end=False,
            )

            BrandingSettings.objects.create(
                user=user,
                watermark_enabled=True,
                watermark_text="Pixeo",
            )
            HomepageSettings.objects.create(
                user=user,
                brand_name=normalized_branding,
            )

            return user
    except IntegrityError as exc:
        # Course entre la validation d'unicité et l'insertion : la contrainte
        # de base reste l'arbitre final.
        raise RegistrationConflict() from exc
    except DjangoValidationError as exc:
        # Le manager appelle full_clean(). Une valeur déjà validée par le
        # serializer ne peut normalement plus échouer ici, sauf en cas de
        # concurrence sur l'e-mail ou le nom public.
        raise RegistrationConflict() from exc
