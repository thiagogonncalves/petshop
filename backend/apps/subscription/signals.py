"""
Signals para criar Subscription ao criar CompanySettings
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from apps.users.models import CompanySettings
from .models import Subscription, Plan, SubscriptionStatus


@receiver(post_save, sender=CompanySettings)
def create_subscription_on_company_created(sender, instance, created, **kwargs):
    """Ao criar CompanySettings, cria Subscription com trial de 7 dias."""
    if created:
        today = timezone.localdate()
        trial_end = today + timedelta(days=7)
        plan = Plan.objects.filter(is_active=True).first()
        Subscription.objects.get_or_create(
            company=instance,
            defaults={
                'plan': plan,
                'status': SubscriptionStatus.TRIAL,
                'trial_start': today,
                'trial_end': trial_end,
            }
        )
