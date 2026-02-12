# Migration para teste de pagamento: preço em R$ 1,00

from django.db import migrations


def set_price_1(apps, schema_editor):
    Plan = apps.get_model('subscription', 'Plan')
    Plan.objects.filter(is_active=True).update(price=1.00)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_update_plan_price_149'),
    ]

    operations = [
        migrations.RunPython(set_price_1, reverse_noop),
    ]
