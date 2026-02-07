"""
Product serializers
"""
from rest_framework import serializers
from .models import Category, Product, StockMovement, Purchase, PurchaseItem
from .services import calculate_sale_price
from decimal import Decimal


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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'barcode', 'sku', 'gtin', 'unit',
            'cost_price', 'profit_margin', 'sale_price', 'price_manually_set',
            'price_per_kg',
            'stock_quantity', 'min_stock', 'is_low_stock',
            'image', 'image_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductPdvSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PDV: search and by-code."""
    stock_balance = serializers.IntegerField(source='stock_quantity', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'gtin', 'unit', 'sale_price', 'price_per_kg', 'stock_balance', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductPricingSerializer(serializers.Serializer):
    """PATCH pricing: profit_margin or sale_price + price_manually_set."""
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0'), required=False)
    sale_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'), required=False)
    price_manually_set = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if 'profit_margin' in attrs and ('sale_price' in attrs or attrs.get('price_manually_set')):
            raise serializers.ValidationError(
                'Use apenas profit_margin OU sale_price com price_manually_set.'
            )
        return attrs

    def update(self, instance, validated_data):
        if 'profit_margin' in validated_data:
            instance.profit_margin = validated_data['profit_margin']
            instance.price_manually_set = False
            instance.recalculate_sale_price()
        if 'sale_price' in validated_data:
            instance.sale_price = validated_data['sale_price']
        if 'price_manually_set' in validated_data:
            instance.price_manually_set = validated_data['price_manually_set']
        instance.save()
        return instance


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type',
            'movement_type_display', 'quantity', 'cost_price', 'reference',
            'previous_stock', 'new_stock', 'observation', 'created_at', 'created_by', 'created_by_name'
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
        else:
            new_stock = quantity

        product.stock_quantity = new_stock
        product.save(update_fields=['stock_quantity'])

        validated_data['previous_stock'] = previous_stock
        validated_data['new_stock'] = new_stock
        validated_data['created_by'] = self.context['request'].user

        return super().create(validated_data)


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_cost', 'total_cost']


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'supplier_name', 'nfe_key', 'nfe_number', 'total_value', 'created_at', 'items']
