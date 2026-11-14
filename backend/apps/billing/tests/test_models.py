"""Tests des plans et abonnements Pixeo."""

from __future__ import annotations

import importlib

import pytest
from django.apps import apps
from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.billing.models import Plan, Subscription, SubscriptionStatus

seed_free_plan = importlib.import_module(
    "apps.billing.migrations.0002_seed_free_plan"
).seed_free_plan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        email="billing@example.com",
        password="StrongPassword123!",
        branding_username="billing-user",
    )


@pytest.fixture
def plan():
    plan, _created = Plan.objects.get_or_create(
        code="free",
        defaults={
            "name": "Free",
            "price_monthly_fcfa": 0,
            "storage_limit_bytes": 5 * 1024 * 1024 * 1024,
        },
    )
    return plan


def test_plan_code_is_unique(plan):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Plan.objects.create(code="free", name="Duplicate")


def test_subscription_defaults(user, plan):
    subscription = Subscription.objects.create(user=user, plan=plan)

    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.current_period_start is not None
    assert subscription.current_period_end is None
    assert subscription.cancel_at_period_end is False


def test_user_cannot_have_two_active_subscriptions(user, plan):
    Subscription.objects.create(user=user, plan=plan)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Subscription.objects.create(user=user, plan=plan)


def test_seed_free_plan_creates_the_initial_plan():
    seed_free_plan(apps, None)

    plan = Plan.objects.get(code="free")
    assert plan.name == "Free"
    assert plan.price_monthly_fcfa == 0
    assert plan.storage_limit_bytes == 5 * 1024 * 1024 * 1024
    assert plan.is_active is True
    assert "Pixeo watermark" in plan.features
