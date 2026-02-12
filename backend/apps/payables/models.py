"""
Contas a pagar
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BillPayable(models.Model):
    """
    Conta a pagar
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Em atraso'),
        ('cancelled', 'Cancelado'),
    ]

    description = models.CharField(max_length=200, verbose_name='Descrição')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor (R$)'
    )
    due_date = models.DateField(verbose_name='Data de vencimento')
    paid_date = models.DateField(null=True, blank=True, verbose_name='Data do pagamento')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    provider = models.CharField(max_length=150, blank=True, verbose_name='Fornecedor')
    observations = models.TextField(blank=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Conta a pagar'
        verbose_name_plural = 'Contas a pagar'
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.description} - R$ {self.amount}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        today = timezone.localdate()
        if self.status == 'pending' and self.due_date < today:
            self.status = 'overdue'
        super().save(*args, **kwargs)
