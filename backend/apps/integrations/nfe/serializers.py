"""
NFe Import serializers
"""
from rest_framework import serializers
from decimal import Decimal
from .models import NFeImport, NFeImportItem
from apps.products.models import Product, Category
from apps.products.services import calculate_sale_price


class NFeImportItemSerializer(serializers.ModelSerializer):
    """Item from NF-e (parsed or DB)."""
    calculated_sale_price = serializers.SerializerMethodField()

    class Meta:
        model = NFeImportItem
        fields = [
            'id', 'product_name', 'quantity', 'unit', 'unit_cost', 'total_cost', 'gtin',
            'product', 'calculated_sale_price'
        ]
        read_only_fields = ['id']

    def get_calculated_sale_price(self, obj):
        margin = self.context.get('profit_margins', {}).get(obj.id) or Decimal('0')
        return str(calculate_sale_price(obj.unit_cost, margin))


class NFeImportSerializer(serializers.ModelSerializer):
    """NFe import header with items."""
    items = NFeImportItemSerializer(many=True, read_only=True)

    class Meta:
        model = NFeImport
        fields = [
            'id', 'access_key', 'supplier_name', 'nfe_number', 'status',
            'imported_at', 'imported_by', 'items'
        ]
        read_only_fields = ['id', 'imported_at', 'imported_by']


