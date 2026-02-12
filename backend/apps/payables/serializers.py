from rest_framework import serializers
from .models import BillPayable


class BillPayableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BillPayable
        fields = [
            'id', 'description', 'amount', 'due_date', 'paid_date',
            'status', 'status_display', 'provider', 'observations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
