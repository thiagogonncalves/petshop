"""
Models para cobrança de plano com trial
"""
from django.db import models
from django.utils import timezone
from apps.users.models import CompanySettings


class Plan(models.Model):
    """Plano de assinatura disponível."""
    name = models.CharField(max_length=100, verbose_name='Nome')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Preço mensal (R$)'
    )
    description = models.TextField(blank=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'

    def __str__(self):
        return f"{self.name} - R$ {self.price}/mês"


class SubscriptionStatus(models.TextChoices):
    TRIAL = 'trial', 'Período de teste'
    ACTIVE = 'active', 'Ativo'
    EXPIRED = 'expired', 'Expirado'
    CANCELLED = 'cancelled', 'Cancelado'


class Subscription(models.Model):
    """
    Assinatura da organização (CompanySettings).
    Uma assinatura por empresa. Nunca apagamos, apenas alteramos status.
    """
    company = models.OneToOneField(
        CompanySettings,
        on_delete=models.PROTECT,
        related_name='subscription',
        verbose_name='Empresa'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        null=True,
        blank=True,
        verbose_name='Plano'
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
        verbose_name='Status'
    )
    trial_start = models.DateField(null=True, blank=True, verbose_name='Início do trial')
    trial_end = models.DateField(null=True, blank=True, verbose_name='Fim do trial')
    current_period_start = models.DateField(null=True, blank=True, verbose_name='Início do período atual')
    current_period_end = models.DateField(null=True, blank=True, verbose_name='Fim do período atual')
    mp_preference_id = models.CharField(max_length=100, blank=True, verbose_name='ID preferência MP')
    mp_payment_id = models.CharField(max_length=100, blank=True, verbose_name='ID pagamento MP')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

    def __str__(self):
        return f"Assinatura {self.company.name or 'Empresa'} - {self.get_status_display()}"

    @property
    def can_write(self):
        """Pode criar/editar: status ACTIVE ou trial dentro do prazo."""
        if self.status == SubscriptionStatus.ACTIVE:
            if self.current_period_end and timezone.localdate() > self.current_period_end:
                return False
            return True
        if self.status == SubscriptionStatus.TRIAL and self.trial_end:
            return timezone.localdate() <= self.trial_end
        return False

    @property
    def days_remaining_trial(self):
        """Dias restantes do trial. 0 se expirado ou não em trial."""
        if self.status != SubscriptionStatus.TRIAL or not self.trial_end:
            return 0
        today = timezone.localdate()
        delta = (self.trial_end - today).days
        return max(0, delta)
