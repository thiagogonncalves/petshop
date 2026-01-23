"""
Client models
"""
from django.db import models
from django.core.validators import RegexValidator
import re


def validate_cpf(value):
    """Validate Brazilian CPF"""
    cpf = re.sub(r'[^0-9]', '', value)
    if len(cpf) != 11:
        raise models.ValidationError('CPF deve ter 11 dígitos')
    if cpf == cpf[0] * 11:
        raise models.ValidationError('CPF inválido')


def validate_cnpj(value):
    """Validate Brazilian CNPJ"""
    cnpj = re.sub(r'[^0-9]', '', value)
    if len(cnpj) != 14:
        raise models.ValidationError('CNPJ deve ter 14 dígitos')


class Client(models.Model):
    """
    Client model
    """
    DOCUMENT_TYPE_CHOICES = [
        ('cpf', 'CPF'),
        ('cnpj', 'CNPJ'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nome')
    document_type = models.CharField(
        max_length=4,
        choices=DOCUMENT_TYPE_CHOICES,
        default='cpf',
        verbose_name='Tipo de Documento'
    )
    document = models.CharField(
        max_length=18,
        unique=True,
        verbose_name='CPF/CNPJ',
        help_text='Apenas números'
    )
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato de telefone inválido")],
        verbose_name='Telefone'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    
    # Address
    street = models.CharField(max_length=200, blank=True, verbose_name='Rua')
    number = models.CharField(max_length=20, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    state = models.CharField(max_length=2, blank=True, verbose_name='Estado')
    zip_code = models.CharField(max_length=10, blank=True, verbose_name='CEP')
    
    observations = models.TextField(blank=True, verbose_name='Observações')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_clients',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.document}"

    def clean(self):
        if self.document_type == 'cpf':
            validate_cpf(self.document)
        elif self.document_type == 'cnpj':
            validate_cnpj(self.document)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
