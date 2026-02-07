# Generated migration - creates default plan and subscription for existing company

from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def create_default_plan_and_subscription(apps, schema_editor):
    Plan = apps.get_model('subscription', 'Plan')
    Subscription = apps.get_model('subscription', 'Subscription')
    CompanySettings = apps.get_model('users', 'CompanySettings')

    # Criar plano padrão se não existir
    plan, _ = Plan.objects.get_or_create(
        name='Plano Mensal',
        defaults={
            'price': 149.90,
            'description': 'Acesso completo ao sistema de gestão para pet shop',
            'is_active': True,
        }
    )

    # Criar assinatura para CompanySettings existente
    company = CompanySettings.objects.first()
    if company:
        today = timezone.localdate()
        trial_end = today + timedelta(days=7)
        Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan': plan,
                'status': 'trial',
                'trial_start': today,
                'trial_end': trial_end,
            }
        )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_plan_and_subscription, reverse_noop),
    ]
