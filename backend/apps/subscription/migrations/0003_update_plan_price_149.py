# Migration to update default plan price to R$ 149.90

from django.db import migrations


def update_plan_price(apps, schema_editor):
    Plan = apps.get_model('subscription', 'Plan')
    Plan.objects.filter(name='Plano Mensal').update(price=149.90)
    # Also update any other active plans if we want consistency
    Plan.objects.filter(is_active=True).exclude(name='Plano Mensal').update(price=149.90)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_create_default_plan'),
    ]

    operations = [
        migrations.RunPython(update_plan_price, reverse_noop),
    ]
