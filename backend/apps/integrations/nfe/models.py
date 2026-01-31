"""
NFe Import models - NF-e XML import and items.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class NFeImport(models.Model):
    """NF-e import header (one XML = one import)."""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ]

    access_key = models.CharField(max_length=44, unique=True, verbose_name='Chave de Acesso')
    xml_file = models.FileField(upload_to='nfe/xml/', blank=True, null=True, verbose_name='Arquivo XML')
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name='Importado em')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    supplier_name = models.CharField(max_length=200, blank=True, verbose_name='Fornecedor (emitente)')
    nfe_number = models.CharField(max_length=20, blank=True, verbose_name='Número NF-e')
    imported_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='nfe_imports',
        verbose_name='Importado por'
    )

    class Meta:
        verbose_name = 'Importação NF-e'
        verbose_name_plural = 'Importações NF-e'
        ordering = ['-imported_at']

    def __str__(self):
        return f"NF-e {self.access_key[:20]}... - {self.status}"


class NFeImportItem(models.Model):
    """Item parsed from NF-e (prod/det)."""
    nfe_import = models.ForeignKey(
        NFeImport,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Importação NF-e'
    )
    product_name = models.CharField(max_length=200, verbose_name='Nome do produto (xProd)')
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Quantidade'
    )
    unit = models.CharField(max_length=10, default='UN', verbose_name='Unidade')
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo unitário'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo total'
    )
    gtin = models.CharField(max_length=14, blank=True, null=True, verbose_name='GTIN/EAN (cEAN)')
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nfe_import_items',
        verbose_name='Produto vinculado'
    )

    class Meta:
        verbose_name = 'Item da Importação NF-e'
        verbose_name_plural = 'Itens da Importação NF-e'
        ordering = ['id']

    def __str__(self):
        return f"{self.product_name} - {self.quantity} x R$ {self.unit_cost}"
