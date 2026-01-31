"""
Sales and Billing models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Sale(models.Model):
    """
    Sale model
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Transferência Bancária'),
        ('installment', 'Parcelado'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='sales',
        null=True,
        blank=True,
        verbose_name='Cliente'
    )
    is_walk_in = models.BooleanField(default=False, verbose_name='Venda avulsa')
    cpf = models.CharField(max_length=14, blank=True, verbose_name='CPF (auditoria avulsa)')
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name='Data da Venda')
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Forma de Pagamento'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    observations = models.TextField(blank=True, verbose_name='Observações')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='created_sales',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['sale_date']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        name = self.client.name if self.client else ('Avulsa' if self.is_walk_in else '-')
        return f"Venda #{self.id} - {name} - R$ {self.total}"

    def calculate_total(self):
        """Calculate total from items"""
        subtotal = sum(item.total for item in self.items.all())
        self.subtotal = subtotal
        self.total = subtotal - self.discount
        return self.total

    def save(self, *args, **kwargs):
        if self.pk:  # Update existing sale
            self.calculate_total()
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    """
    Sale Item model (products or services)
    """
    ITEM_TYPE_CHOICES = [
        ('product', 'Produto'),
        ('service', 'Serviço'),
    ]
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Venda'
    )
    item_type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES,
        verbose_name='Tipo de Item'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sale_items',
        verbose_name='Produto'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sale_items',
        verbose_name='Serviço'
    )
    appointment = models.ForeignKey(
        'scheduling.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sale_items',
        verbose_name='Agendamento'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Quantidade'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Unitário'
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Total'
    )

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'
        ordering = ['id']
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        item_name = self.product.name if self.product else self.service.name
        return f"{item_name} - {self.quantity}x R$ {self.unit_price}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.item_type == 'product' and not self.product:
            raise ValidationError('Produto é obrigatório para item do tipo produto')
        if self.item_type == 'service' and not self.service:
            raise ValidationError('Serviço é obrigatório para item do tipo serviço')
        if self.item_type == 'product' and self.service:
            raise ValidationError('Não pode ter produto e serviço no mesmo item')
        if self.item_type == 'service' and self.product:
            raise ValidationError('Não pode ter produto e serviço no mesmo item')

    def calculate_total(self):
        """Calculate item total"""
        self.total = (self.unit_price * self.quantity) - self.discount
        return self.total

    def save(self, *args, **kwargs):
        self.clean()
        self.calculate_total()
        super().save(*args, **kwargs)
        # Update sale total
        if self.sale:
            self.sale.calculate_total()
            self.sale.save()


class Receipt(models.Model):
    """
    Receipt model
    """
    sale = models.OneToOneField(
        Sale,
        on_delete=models.CASCADE,
        related_name='receipt',
        verbose_name='Venda'
    )
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='Número do Recibo')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Emitido em')
    pdf_file = models.FileField(upload_to='receipts/', blank=True, null=True, verbose_name='PDF')

    class Meta:
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'
        ordering = ['-issued_at']

    def __str__(self):
        return f"Recibo #{self.receipt_number} - Venda #{self.sale.id}"


class Invoice(models.Model):
    """
    Invoice model
    """
    sale = models.OneToOneField(
        Sale,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name='Venda'
    )
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='Número da Nota')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Emitida em')
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True, verbose_name='PDF')

    class Meta:
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        ordering = ['-issued_at']

    def __str__(self):
        return f"Nota #{self.invoice_number} - Venda #{self.sale.id}"
