"""
Sales serializers
"""
from decimal import Decimal
from rest_framework import serializers
from .models import Sale, SaleItem, Receipt, Invoice, CreditAccount, CreditInstallment


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer for SaleItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'item_type', 'item_type_display', 'product', 'product_name',
            'service', 'service_name', 'appointment', 'quantity',
            'sold_by_kg',
            'unit_price', 'discount', 'total'
        ]
        read_only_fields = ['id', 'total']

    def validate(self, attrs):
        if attrs['item_type'] == 'product' and not attrs.get('product'):
            raise serializers.ValidationError({'product': 'Produto é obrigatório para item do tipo produto'})
        if attrs['item_type'] == 'service' and not attrs.get('service'):
            raise serializers.ValidationError({'service': 'Serviço é obrigatório para item do tipo serviço'})
        
        # Validate stock availability for products
        if attrs['item_type'] == 'product' and attrs.get('product'):
            product = attrs['product']
            quantity = attrs.get('quantity', 1)
            sold_by_kg = attrs.get('sold_by_kg', False)
            if product.unit == 'KG' and sold_by_kg:
                qty_grams = int(round(float(quantity) * 1000))
                stock_needed = qty_grams
            else:
                qty_int = int(quantity) if quantity == int(quantity) else int(round(float(quantity)))
                stock_needed = qty_int
            
            if self.instance:
                old_qty = self.instance.quantity
                old_sold_kg = getattr(self.instance, 'sold_by_kg', False)
                if product.unit == 'KG' and old_sold_kg:
                    old_needed = int(round(float(old_qty) * 1000))
                else:
                    old_needed = int(old_qty) if old_qty == int(old_qty) else int(round(float(old_qty)))
                quantity_diff = stock_needed - old_needed
                if quantity_diff > 0 and product.stock_quantity < quantity_diff:
                    raise serializers.ValidationError({
                        'quantity': f'Estoque insuficiente. Disponível: {product.stock_quantity}'
                    })
            else:
                if product.stock_quantity < stock_needed:
                    raise serializers.ValidationError({
                        'quantity': f'Estoque insuficiente. Disponível: {product.stock_quantity}'
                    })
        
        return attrs


class SaleSerializer(serializers.ModelSerializer):
    """Serializer for Sale model"""
    items = SaleItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'client', 'client_name', 'sale_date', 'items',
            'subtotal', 'discount', 'total', 'payment_method',
            'payment_method_display', 'status', 'status_display',
            'observations', 'cancellation_reason', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'sale_date', 'subtotal', 'total', 'created_at', 'updated_at', 'created_by']


class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sales with items"""
    items = SaleItemSerializer(many=True)
    
    class Meta:
        model = Sale
        fields = [
            'client', 'items', 'discount', 'payment_method',
            'status', 'observations'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['created_by'] = self.context['request'].user
        
        sale = Sale.objects.create(**validated_data)
        
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)
        
        sale.calculate_total()
        sale.save()
        
        return sale


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for Receipt model"""
    sale_data = SaleSerializer(source='sale', read_only=True)
    
    class Meta:
        model = Receipt
        fields = ['id', 'sale', 'sale_data', 'receipt_number', 'issued_at', 'pdf_file']
        read_only_fields = ['id', 'receipt_number', 'issued_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    sale_data = SaleSerializer(source='sale', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'sale', 'sale_data', 'invoice_number', 'issued_at', 'pdf_file']
        read_only_fields = ['id', 'invoice_number', 'issued_at']


class PdvSaleItemInputSerializer(serializers.Serializer):
    """Input for PDV sale item (product only)."""
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=4, min_value=Decimal('0.0001'))
    sold_by_kg = serializers.BooleanField(required=False, default=False)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'),
        required=False, default=Decimal('0.00')
    )


class PdvSalePaymentInputSerializer(serializers.Serializer):
    """Uma parcela de pagamento: forma + valor."""
    payment_method = serializers.ChoiceField(
        choices=[c for c in Sale.PAYMENT_METHOD_CHOICES if c[0] not in ('crediario', 'mixed')]
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class PdvSaleCreateSerializer(serializers.Serializer):
    """Create and finalize a PDV sale in one request."""
    cpf = serializers.CharField(required=False, allow_blank=True)
    client_cpf = serializers.CharField(required=False, allow_blank=True)
    is_walk_in = serializers.BooleanField(default=False)
    items = PdvSaleItemInputSerializer(many=True)
    payment_method = serializers.ChoiceField(
        choices=Sale.PAYMENT_METHOD_CHOICES,
        required=False,
    )
    payments = PdvSalePaymentInputSerializer(many=True, required=False)
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'),
        required=False, default=Decimal('0.00')
    )
    # Crediário fields (when payment_method=crediario)
    down_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'),
        required=False, default=Decimal('0.00')
    )
    installments_count = serializers.IntegerField(
        min_value=1, max_value=12, required=False
    )
    first_due_date = serializers.DateField(required=False)
    change_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'),
        required=False, default=Decimal('0.00')
    )
    cash_received = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'),
        required=False, allow_null=True
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Pelo menos um item é obrigatório.')
        return value

    def validate(self, attrs):
        payments = attrs.get('payments') or []
        payment_method = attrs.get('payment_method')
        if payments:
            if payment_method == 'crediario':
                raise serializers.ValidationError({
                    'payments': 'Pagamento fracionado não permitido com crediário.'
                })
            total_paid = sum(Decimal(str(p['amount'])) for p in payments)
            if total_paid <= 0:
                raise serializers.ValidationError({
                    'payments': 'Informe pelo menos um pagamento com valor maior que zero.'
                })
            attrs['_payments_total'] = total_paid
        else:
            if not payment_method:
                raise serializers.ValidationError({
                    'payment_method': 'Informe a forma de pagamento ou os pagamentos fracionados.'
                })
        payment_method = payment_method or (payments[0]['payment_method'] if payments else None)
        is_walk_in = attrs.get('is_walk_in', True)

        if payment_method == 'crediario':
            # Crediário: client required, no walk-in
            cpf_raw = (attrs.get('client_cpf') or attrs.get('cpf') or '').strip()
            cpf_digits = ''.join(c for c in cpf_raw if c.isdigit())
            if len(cpf_digits) != 11:
                raise serializers.ValidationError({
                    'cpf': 'Crediário exige cliente cadastrado. Informe CPF válido (11 dígitos).'
                })
            if is_walk_in:
                raise serializers.ValidationError({
                    'is_walk_in': 'Venda avulsa não permitida no crediário. Selecione um cliente.'
                })
            inst_count = attrs.get('installments_count', 0)
            if inst_count < 1 or inst_count > 12:
                raise serializers.ValidationError({
                    'installments_count': 'Número de parcelas deve ser entre 1 e 12.'
                })
            if not attrs.get('first_due_date'):
                raise serializers.ValidationError({
                    'first_due_date': 'Data do primeiro vencimento é obrigatória.'
                })
        else:
            # Other payment methods
            if not is_walk_in:
                cpf = (attrs.get('cpf') or '').strip()
                cpf_digits = ''.join(c for c in cpf if c.isdigit())
                if len(cpf_digits) != 11:
                    raise serializers.ValidationError({
                        'cpf': 'Informe um CPF válido (11 dígitos) ou marque Venda avulsa.'
                    })
        return attrs


# --- Crediário serializers ---

class CreditInstallmentSerializer(serializers.ModelSerializer):
    """Serializer for CreditInstallment"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    paid_by_name = serializers.CharField(source='paid_by.username', read_only=True)

    class Meta:
        model = CreditInstallment
        fields = [
            'id', 'number', 'due_date', 'amount', 'status', 'status_display',
            'paid_at', 'paid_amount', 'payment_method', 'payment_method_display',
            'paid_by', 'paid_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'number', 'due_date', 'amount', 'created_at']


class CreditAccountSerializer(serializers.ModelSerializer):
    """Serializer for CreditAccount list/detail"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_document = serializers.CharField(source='client.document', read_only=True)
    sale_id = serializers.IntegerField(source='sale.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    installments = CreditInstallmentSerializer(many=True, read_only=True)
    next_due_date = serializers.DateField(read_only=True)
    pending_count = serializers.IntegerField(read_only=True)
    overdue_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CreditAccount
        fields = [
            'id', 'sale', 'sale_id', 'client', 'client_name', 'client_document',
            'total_amount', 'down_payment', 'financed_amount', 'installments_count',
            'status', 'status_display', 'installments',
            'next_due_date', 'pending_count', 'overdue_count',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = fields


class CreditAccountListSerializer(serializers.ModelSerializer):
    """Light serializer for CreditAccount list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    sale_id = serializers.IntegerField(source='sale.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CreditAccount
        fields = [
            'id', 'sale_id', 'client', 'client_name', 'total_amount',
            'financed_amount', 'installments_count',
            'status', 'status_display',
            'next_due_date', 'pending_count', 'overdue_count',
            'created_at'
        ]


class PayInstallmentSerializer(serializers.Serializer):
    """Payload for paying an installment"""
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.01'),
        required=False
    )
    paid_at = serializers.DateTimeField(required=False)
    payment_method = serializers.ChoiceField(
        choices=[
            ('cash', 'Dinheiro'),
            ('credit_card', 'Cartão de Crédito'),
            ('debit_card', 'Cartão de Débito'),
            ('pix', 'PIX'),
            ('bank_transfer', 'Transferência Bancária'),
        ],
        required=True,
        error_messages={'required': 'Informe a forma de pagamento.'},
    )
