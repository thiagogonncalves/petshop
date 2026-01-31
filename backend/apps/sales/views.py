"""
Sales views
"""
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from .models import Sale, SaleItem, Receipt, Invoice
from .serializers import (
    SaleSerializer, SaleCreateSerializer,
    SaleItemSerializer, ReceiptSerializer, InvoiceSerializer,
    PdvSaleCreateSerializer,
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

    @action(detail=False, methods=['post'], url_path='pdv')
    def pdv_create(self, request):
        """
        PDV: create and finalize sale in one request.
        Body: { cpf?, is_walk_in, items: [{product_id, quantity, unit_price}], payment_method }
        Creates sale (status=paid), deducts stock in transaction.
        """
        serializer = PdvSaleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cpf_raw = (data.get('cpf') or '').strip()
        cpf_digits = re.sub(r'[^0-9]', '', cpf_raw)
        is_walk_in = data.get('is_walk_in', True)
        items_data = data['items']
        payment_method = data['payment_method']

        client = None
        cpf_saved = ''
        if not is_walk_in and cpf_digits:
            from apps.clients.models import Client
            client = Client.objects.filter(is_active=True, document_type='cpf', document=cpf_digits).first()
            if not client:
                return Response(
                    {'cpf': 'Cliente não encontrado com este CPF. Cadastre o cliente ou marque Venda avulsa.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if is_walk_in and cpf_digits:
            cpf_saved = cpf_digits

        from apps.products.models import Product, StockMovement

        with transaction.atomic():
            sale = Sale.objects.create(
                client=client,
                is_walk_in=is_walk_in,
                cpf=cpf_saved,
                discount=0,
                total=0,
                payment_method=payment_method,
                status='paid',
                created_by=request.user,
            )
            for item_data in items_data:
                product = Product.objects.select_for_update().filter(pk=item_data['product_id']).first()
                if not product:
                    return Response(
                        {'items': f'Produto id {item_data["product_id"]} não encontrado.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                qty = item_data['quantity']
                if product.stock_quantity < qty:
                    return Response(
                        {'items': f'Estoque insuficiente para {product.name}. Disponível: {product.stock_quantity}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                unit_price = item_data['unit_price']
                SaleItem.objects.create(
                    sale=sale,
                    item_type='product',
                    product=product,
                    quantity=qty,
                    unit_price=unit_price,
                    discount=0,
                )
                prev = product.stock_quantity
                product.stock_quantity = prev - qty
                product.save(update_fields=['stock_quantity'])
                StockMovement.objects.create(
                    product=product,
                    movement_type='exit',
                    quantity=qty,
                    previous_stock=prev,
                    new_stock=product.stock_quantity,
                    reference=f'Venda #{sale.id}',
                    observation=f'Saída por venda PDV #{sale.id}',
                    created_by=request.user,
                )
            sale.calculate_total()
            sale.save()

        out = SaleSerializer(sale)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='receipt')
    def receipt(self, request, pk=None):
        """Return structured data for thermal receipt (80mm)."""
        sale = self.get_object()
        items = []
        for item in sale.items.all():
            name = (item.product.name if item.product else (item.service.name if item.service else '-'))
            items.append({
                'name': name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total': str(item.total),
            })
        client_label = 'Venda avulsa'
        if sale.client:
            client_label = f'{sale.client.name} - CPF: {sale.cpf or sale.client.document}'
        elif sale.cpf:
            client_label = f'CPF: {sale.cpf} (avulsa)'
        payload = {
            'sale_id': sale.id,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'items': items,
            'subtotal': str(sale.subtotal),
            'discount': str(sale.discount),
            'total': str(sale.total),
            'client': client_label,
            'payment_method': sale.get_payment_method_display(),
        }
        return Response(payload)


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
