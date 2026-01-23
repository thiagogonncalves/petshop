"""
Sales serializers
"""
from rest_framework import serializers
from .models import Sale, SaleItem, Receipt, Invoice


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
            
            # Check if updating existing item
            if self.instance:
                old_quantity = self.instance.quantity
                # Calculate the difference
                quantity_diff = quantity - old_quantity
                
                # Only check stock if we're increasing quantity
                if quantity_diff > 0 and product.stock_quantity < quantity_diff:
                    raise serializers.ValidationError({
                        'quantity': f'Estoque insuficiente. Disponível: {product.stock_quantity}, Solicitado: {quantity_diff}'
                    })
            else:
                # New item - check if stock is available
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError({
                        'quantity': f'Estoque insuficiente. Disponível: {product.stock_quantity}, Solicitado: {quantity}'
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
            'observations', 'created_at', 'updated_at',
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
