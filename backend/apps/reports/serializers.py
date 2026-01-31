"""
Serializers for report responses (read-only, dict/list data).
"""
from rest_framework import serializers
from apps.sales.models import Sale


class ReportSaleListSerializer(serializers.ModelSerializer):
    """Minimal sale for report list: id, date, seller, client, total, payment, status."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    client_name = serializers.SerializerMethodField()
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'sale_date', 'created_by', 'created_by_name',
            'client', 'client_name', 'total', 'payment_method',
            'payment_method_display', 'status', 'status_display',
        ]

    def get_client_name(self, obj):
        if obj.client:
            return obj.client.name
        return 'Avulsa' if obj.is_walk_in else '-'
