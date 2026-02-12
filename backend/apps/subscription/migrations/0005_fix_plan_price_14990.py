# Corrige preço do plano para R$ 149,90 (era R$ 1,00 de teste)

from django.db import migrations


def fix_plan_price(apps, schema_editor):
    Plan = apps.get_model('subscription', 'Plan')
    Plan.objects.filter(is_active=True).update(price=149.90)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_plan_price_test_1'),
    ]

    operations = [
        migrations.RunPython(fix_plan_price, reverse_noop),
    ]
