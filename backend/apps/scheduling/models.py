"""
Scheduling models
"""
from django.db import models
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    """
    Appointment/Scheduling model
    """
    STATUS_CHOICES = [
        ('scheduled', 'Agendado'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),  # legado
        ('done', 'Concluído'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'Não Compareceu'),
    ]

    CREATED_VIA_CHOICES = [
        ('admin', 'Administrador/Atendente'),
        ('client_self', 'Cliente (autoagendamento)'),
    ]
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Cliente'
    )
    pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Animal'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='Serviço'
    )
    scheduled_date = models.DateTimeField(verbose_name='Data e Hora Agendada', blank=True, null=True)
    start_at = models.DateTimeField(verbose_name='Início')
    end_at = models.DateTimeField(verbose_name='Término')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    observations = models.TextField(blank=True, verbose_name='Observações')
    created_via = models.CharField(
        max_length=15,
        choices=CREATED_VIA_CHOICES,
        default='admin',
        verbose_name='Criado via'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_appointments',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-start_at']
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['pet']),
            models.Index(fields=['service']),
            models.Index(fields=['start_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.pet.name} - {self.service.name} - {self.start_at}"

    def clean(self):
        if self.pet and self.client and self.pet.client != self.client:
            raise ValidationError('O animal deve pertencer ao cliente selecionado')
        if self.start_at and self.end_at and self.start_at >= self.end_at:
            raise ValidationError('Data/hora de término deve ser posterior ao início')

    def save(self, *args, **kwargs):
        self.clean()
        if self.start_at and not self.scheduled_date:
            self.scheduled_date = self.start_at
        super().save(*args, **kwargs)


class BusinessHoursConfig(models.Model):
    """Configuração única de horário de funcionamento."""
    slot_minutes = models.PositiveIntegerField(default=30, verbose_name='Intervalo do slot (min)')
    timezone = models.CharField(max_length=50, default='America/Fortaleza', verbose_name='Fuso horário')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Config. Horário de Funcionamento'
        verbose_name_plural = 'Config. Horários de Funcionamento'

    def __str__(self):
        return f"Slots de {self.slot_minutes}min - {self.timezone}"


class BusinessHoursRule(models.Model):
    """Regra de funcionamento por dia da semana (0=Segunda ... 6=Domingo)."""
    config = models.ForeignKey(
        BusinessHoursConfig,
        on_delete=models.CASCADE,
        related_name='rules',
        verbose_name='Configuração'
    )
    weekday = models.PositiveSmallIntegerField(verbose_name='Dia (0=Seg...6=Dom)')
    is_open = models.BooleanField(default=True, verbose_name='Aberto')
    open_time = models.TimeField(null=True, blank=True, verbose_name='Abertura')
    close_time = models.TimeField(null=True, blank=True, verbose_name='Fechamento')
    break_start = models.TimeField(null=True, blank=True, verbose_name='Início pausa')
    break_end = models.TimeField(null=True, blank=True, verbose_name='Fim pausa')

    class Meta:
        verbose_name = 'Regra de Horário'
        verbose_name_plural = 'Regras de Horário'
        unique_together = [('config', 'weekday')]
        ordering = ['weekday']

    def __str__(self):
        d = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][self.weekday]
        if not self.is_open:
            return f"{d}: Fechado"
        return f"{d}: {self.open_time} - {self.close_time}"


class BusinessClosure(models.Model):
    """Datas de fechamento (feriados, folgas)."""
    date = models.DateField(unique=True, verbose_name='Data')
    reason = models.CharField(max_length=200, blank=True, verbose_name='Motivo')

    class Meta:
        verbose_name = 'Fechamento'
        verbose_name_plural = 'Fechamentos'
        ordering = ['date']

    def __str__(self):
        return f"{self.date}: {self.reason or 'Fechado'}"
