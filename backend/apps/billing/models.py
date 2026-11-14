"""Catalogue des plans et abonnements Pixeo.

Le plan actif d'un photographe est porté par ``Subscription``. Le modèle
``User`` ne contient volontairement aucun champ de plan : l'abonnement reste la
source de vérité, y compris pour les évolutions futures (paiement, historique,
changement de formule).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    """Formule commerciale du catalogue Pixeo."""

    code = models.SlugField(_("code"), max_length=50, unique=True)
    name = models.CharField(_("name"), max_length=100)
    price_monthly_fcfa = models.PositiveIntegerField(
        _("monthly price (FCFA)"), default=0
    )
    storage_limit_bytes = models.PositiveBigIntegerField(
        _("storage limit (bytes)"), default=0
    )
    features = models.JSONField(_("features"), default=list, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    TRIALING = "trialing", _("Trialing")
    PAST_DUE = "past_due", _("Past due")
    CANCELED = "canceled", _("Canceled")
    INCOMPLETE = "incomplete", _("Incomplete")


class Subscription(models.Model):
    """Abonnement d'un photographe à un plan Pixeo.

    Un utilisateur ne peut avoir qu'un seul abonnement actif à la fois. Les
    abonnements résiliés restent conservés pour l'historique.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("photographer"),
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("plan"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    current_period_start = models.DateTimeField(
        _("current period start"), default=timezone.now
    )
    current_period_end = models.DateTimeField(
        _("current period end"), null=True, blank=True
    )
    cancel_at_period_end = models.BooleanField(
        _("cancel at period end"), default=False
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=SubscriptionStatus.ACTIVE),
                name="unique_active_subscription_per_user",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.plan.code} ({self.status})"
