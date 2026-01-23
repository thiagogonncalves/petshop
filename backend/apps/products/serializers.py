"""
Product serializers
"""
from rest_framework import serializers
from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    profit_margin = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'barcode', 'sku', 'cost_price', 'sale_price',
            'stock_quantity', 'min_stock', 'unit', 'is_low_stock',
            'profit_margin', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type',
            'movement_type_display', 'quantity', 'previous_stock',
            'new_stock', 'observation', 'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'previous_stock', 'new_stock', 'created_at', 'created_by'
        ]

    def create(self, validated_data):
        product = validated_data['product']
        movement_type = validated_data['movement_type']
        quantity = validated_data['quantity']
        
        previous_stock = product.stock_quantity
        
        if movement_type == 'entry':
            new_stock = previous_stock + quantity
        elif movement_type == 'exit':
            if quantity > previous_stock:
                raise serializers.ValidationError(
                    {'quantity': 'Quantidade maior que estoque disponível'}
                )
            new_stock = previous_stock - quantity
        else:  # adjustment
            new_stock = quantity
        
        product.stock_quantity = new_stock
        product.save()
        
        validated_data['previous_stock'] = previous_stock
        validated_data['new_stock'] = new_stock
        validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)
