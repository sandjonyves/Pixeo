"""Initialise le plan Free utilisé lors de l'inscription."""

from __future__ import annotations

from django.db import migrations

FREE_PLAN_CODE = "free"
FREE_PLAN_DEFAULTS = {
    "name": "Free",
    "price_monthly_fcfa": 0,
    "storage_limit_bytes": 5 * 1024 * 1024 * 1024,
    "features": [
        "5 Go storage",
        "Unlimited galleries",
        "Private client link",
        "Password protection",
        "Pixeo watermark",
    ],
    "is_active": True,
    "sort_order": 0,
}


def seed_free_plan(apps, schema_editor):
    Plan = apps.get_model("billing", "Plan")
    Plan.objects.get_or_create(
        code=FREE_PLAN_CODE,
        defaults=FREE_PLAN_DEFAULTS,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_free_plan, migrations.RunPython.noop),
    ]
