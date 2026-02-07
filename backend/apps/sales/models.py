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
        ('crediario', 'Crediário da Casa'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('credit_open', 'Crediário em aberto'),
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
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Quantidade'
    )
    sold_by_kg = models.BooleanField(
        default=False,
        verbose_name='Vendido por kg'
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
        from decimal import Decimal
        qty = Decimal(str(self.quantity))
        self.total = (self.unit_price * qty) - self.discount
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


class CreditAccount(models.Model):
    """
    Crediário da Casa (Store Credit / Fiado)
    OneToOne with Sale when payment_method=crediario
    """
    STATUS_CHOICES = [
        ('open', 'Em aberto'),
        ('settled', 'Quitado'),
        ('cancelled', 'Cancelado'),
    ]

    sale = models.OneToOneField(
        Sale,
        on_delete=models.CASCADE,
        related_name='credit_account',
        verbose_name='Venda'
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='credit_accounts',
        verbose_name='Cliente'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor total'
    )
    down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Entrada'
    )
    financed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor financiado'
    )
    installments_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Número de parcelas'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Status'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='created_credit_accounts',
        verbose_name='Criado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Crediário'
        verbose_name_plural = 'Crediários'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Crediário #{self.id} - {self.client.name} - R$ {self.financed_amount}"

    @property
    def next_due_date(self):
        """Próxima data de vencimento (parcela pendente mais antiga)"""
        inst = self.installments.filter(status__in=['pending', 'overdue']).order_by('due_date').first()
        return inst.due_date if inst else None

    @property
    def pending_count(self):
        return self.installments.filter(status__in=['pending', 'overdue']).count()

    @property
    def paid_count(self):
        return self.installments.filter(status='paid').count()

    @property
    def overdue_count(self):
        return self.installments.filter(status='overdue').count()


class CreditInstallment(models.Model):
    """
    Parcela do Crediário
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Atrasado'),
        ('cancelled', 'Cancelado'),
    ]

    credit_account = models.ForeignKey(
        CreditAccount,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name='Crediário'
    )
    number = models.PositiveIntegerField(verbose_name='Número da parcela')
    due_date = models.DateField(verbose_name='Data de vencimento')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Data do pagamento')
    payment_method = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Forma de pagamento',
        choices=[
            ('cash', 'Dinheiro'),
            ('credit_card', 'Cartão de Crédito'),
            ('debit_card', 'Cartão de Débito'),
            ('pix', 'PIX'),
            ('bank_transfer', 'Transferência Bancária'),
        ],
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor pago'
    )
    paid_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_installments',
        verbose_name='Pago por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['credit_account', 'number']
        unique_together = [('credit_account', 'number')]
        indexes = [
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"Parcela {self.number}/{self.credit_account.installments_count} - R$ {self.amount}"
