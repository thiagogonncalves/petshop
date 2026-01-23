"""
Sales views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Sale, SaleItem, Receipt, Invoice
from .serializers import (
    SaleSerializer, SaleCreateSerializer,
    SaleItemSerializer, ReceiptSerializer, InvoiceSerializer
)


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Sale management
    """
    queryset = Sale.objects.all()
    filterset_fields = ['client', 'status', 'payment_method']
    search_fields = ['client__name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def get_queryset(self):
        queryset = Sale.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)
        
        return queryset

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to sale"""
        sale = self.get_object()
        serializer = SaleItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sale=sale)
        sale.calculate_total()
        sale.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        """Mark sale as paid and update stock"""
        sale = self.get_object()
        
        if sale.status == 'paid':
            return Response(
                {'error': 'Venda já está paga'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update stock for products
        from apps.products.models import StockMovement
        from django.db import transaction
        
        with transaction.atomic():
            for item in sale.items.filter(item_type='product'):
                if item.product:
                    product = item.product
                    previous_stock = product.stock_quantity
                    new_stock = previous_stock - item.quantity
                    
                    if new_stock < 0:
                        return Response(
                            {'error': f'Estoque insuficiente para o produto {product.name}. Estoque disponível: {previous_stock}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Update product stock
                    product.stock_quantity = new_stock
                    product.save()
                    
                    # Create stock movement record
                    StockMovement.objects.create(
                        product=product,
                        movement_type='exit',
                        quantity=item.quantity,
                        previous_stock=previous_stock,
                        new_stock=new_stock,
                        observation=f'Saída por venda #{sale.id}',
                        created_by=request.user
                    )
            
            sale.status = 'paid'
            sale.save()
        
        serializer = self.get_serializer(sale)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_receipt(self, request, pk=None):
        """Generate receipt for sale"""
        sale = self.get_object()
        receipt, created = Receipt.objects.get_or_create(
            sale=sale,
            defaults={'receipt_number': f'REC-{sale.id}-{timezone.now().strftime("%Y%m%d")}'}
        )
        serializer = ReceiptSerializer(receipt)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_invoice(self, request, pk=None):
        """Generate invoice for sale"""
        sale = self.get_object()
        invoice, created = Invoice.objects.get_or_create(
            sale=sale,
            defaults={'invoice_number': f'NF-{sale.id}-{timezone.now().strftime("%Y%m%d")}'}
        )
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class SaleItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SaleItem management
    """
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Receipt (read-only)
    """
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    filterset_fields = ['sale']
    search_fields = ['receipt_number', 'sale__client__name']


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Invoice (read-only)
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filterset_fields = ['sale']
    search_fields = ['invoice_number', 'sale__client__name']
