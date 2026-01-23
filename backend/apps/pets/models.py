"""
Pet models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Pet(models.Model):
    """
    Pet model
    """
    SPECIES_CHOICES = [
        ('dog', 'Cão'),
        ('cat', 'Gato'),
        ('bird', 'Ave'),
        ('fish', 'Peixe'),
        ('reptile', 'Réptil'),
        ('rodent', 'Roedor'),
        ('other', 'Outro'),
    ]
    
    SEX_CHOICES = [
        ('male', 'Macho'),
        ('female', 'Fêmea'),
        ('unknown', 'Não informado'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    species = models.CharField(
        max_length=10,
        choices=SPECIES_CHOICES,
        verbose_name='Espécie'
    )
    breed = models.CharField(max_length=100, blank=True, verbose_name='Raça')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Peso (kg)'
    )
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES,
        default='unknown',
        verbose_name='Sexo'
    )
    color = models.CharField(max_length=50, blank=True, verbose_name='Cor')
    photo = models.ImageField(upload_to='pets/photos/', blank=True, null=True, verbose_name='Foto')
    observations = models.TextField(blank=True, verbose_name='Observações')
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='pets',
        verbose_name='Cliente'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_pets',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['species']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_species_display()}) - {self.client.name}"

    @property
    def age(self):
        """Calculate age in years"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
