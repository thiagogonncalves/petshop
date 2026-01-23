"""
Product and Inventory models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Product Category model
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model
    """
    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoria'
    )
    barcode = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='Código de Barras')
    sku = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='SKU')
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço de Custo'
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço de Venda'
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Quantidade em Estoque'
    )
    min_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Estoque Mínimo'
    )
    unit = models.CharField(max_length=20, default='un', verbose_name='Unidade')
    
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['stock_quantity']),
        ]

    def __str__(self):
        return f"{self.name} - R$ {self.sale_price}"

    @property
    def is_low_stock(self):
        """Check if product is below minimum stock"""
        return self.stock_quantity <= self.min_stock

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price == 0:
            return 0
        return ((self.sale_price - self.cost_price) / self.cost_price) * 100


class StockMovement(models.Model):
    """
    Stock movement (entry/exit) model
    """
    MOVEMENT_TYPE_CHOICES = [
        ('entry', 'Entrada'),
        ('exit', 'Saída'),
        ('adjustment', 'Ajuste'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name='Produto'
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name='Tipo de Movimentação'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantidade'
    )
    previous_stock = models.IntegerField(verbose_name='Estoque Anterior')
    new_stock = models.IntegerField(verbose_name='Novo Estoque')
    observation = models.TextField(blank=True, verbose_name='Observação')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"
