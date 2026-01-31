"""
Product and Inventory models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP


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
    Product model with smart pricing (cost, margin, sale_price).
    sale_price = cost_price * (1 + profit_margin/100) unless price_manually_set.
    """
    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoria'
    )
    sku = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='SKU')
    barcode = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='Código de Barras')
    gtin = models.CharField(max_length=14, blank=True, null=True, verbose_name='GTIN/EAN')

    unit = models.CharField(max_length=20, default='UN', verbose_name='Unidade')

    # Pricing
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço de Custo'
    )
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Margem de Lucro (%)'
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.01'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço de Venda'
    )
    price_manually_set = models.BooleanField(
        default=False,
        verbose_name='Preço definido manualmente'
    )

    # Inventory (kept in sync with StockMovement balance for performance)
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

    def recalculate_sale_price(self):
        """Recalculate sale_price from cost_price and profit_margin if not manually set."""
        if self.price_manually_set:
            return
        self.sale_price = (self.cost_price * (Decimal('1') + self.profit_margin / Decimal('100'))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        if self.sale_price < Decimal('0.01'):
            self.sale_price = Decimal('0.01')

    def save(self, *args, **kwargs):
        self.recalculate_sale_price()
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """
    Stock movement (entry/exit/adjustment). Balance = sum of movement deltas.
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
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço de Custo (entrada)'
    )
    reference = models.CharField(max_length=200, blank=True, verbose_name='Referência (NF-e, venda, etc)')
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

    @property
    def quantity_delta(self):
        """Delta for balance: + for entry, - for exit, (new - prev) for adjustment."""
        if self.movement_type == 'entry':
            return self.quantity
        if self.movement_type == 'exit':
            return -self.quantity
        return self.new_stock - self.previous_stock

    @classmethod
    def get_stock_balance(cls, product_id):
        """Current stock balance = sum of all movement deltas for product."""
        from django.db.models import Sum, Case, When, IntegerField, F
        agg = cls.objects.filter(product_id=product_id).aggregate(
            total=Sum(
                Case(
                    When(movement_type='entry', then=F('quantity')),
                    When(movement_type='exit', then=-F('quantity')),
                    When(movement_type='adjustment', then=F('new_stock') - F('previous_stock')),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )
        return agg['total'] or 0


class Purchase(models.Model):
    """Purchase / stock entry header (e.g. from NF-e)."""
    supplier_name = models.CharField(max_length=200, verbose_name='Fornecedor')
    nfe_key = models.CharField(max_length=44, unique=True, blank=True, null=True, verbose_name='Chave NF-e')
    nfe_number = models.CharField(max_length=20, blank=True, verbose_name='Número NF-e')
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Total'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchases',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-created_at']

    def __str__(self):
        return f"Compra #{self.id} - {self.supplier_name}"


class PurchaseItem(models.Model):
    """Item of a purchase (product + quantity + cost)."""
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Compra'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_items',
        verbose_name='Produto'
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Quantidade'
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo Unitário'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo Total'
    )

    class Meta:
        verbose_name = 'Item da Compra'
        verbose_name_plural = 'Itens da Compra'
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x R$ {self.unit_cost}"
