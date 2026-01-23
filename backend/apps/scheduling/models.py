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
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'Não Compareceu'),
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
    scheduled_date = models.DateTimeField(verbose_name='Data e Hora Agendada')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    observations = models.TextField(blank=True, verbose_name='Observações')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['pet']),
            models.Index(fields=['service']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.pet.name} - {self.service.name} - {self.scheduled_date}"

    def clean(self):
        # Validate that pet belongs to client
        if self.pet and self.client and self.pet.client != self.client:
            raise ValidationError('O animal deve pertencer ao cliente selecionado')
        
        # Check for overlapping appointments
        if self.pk:  # Updating existing appointment
            overlapping = Appointment.objects.filter(
                scheduled_date=self.scheduled_date,
                status__in=['scheduled', 'in_progress']
            ).exclude(pk=self.pk)
        else:  # Creating new appointment
            overlapping = Appointment.objects.filter(
                scheduled_date=self.scheduled_date,
                status__in=['scheduled', 'in_progress']
            )
        
        if overlapping.exists():
            raise ValidationError('Já existe um agendamento para este horário')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
