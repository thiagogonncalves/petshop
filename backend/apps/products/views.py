"""
Product views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import models
from django.db.models.deletion import ProtectedError
from .models import Category, Product, StockMovement, Purchase
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductPricingSerializer,
    ProductPdvSerializer,
    StockMovementSerializer,
    PurchaseSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category management."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name']


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product management (editável: preço de venda, custo, margem, etc.)."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'barcode', 'sku', 'gtin']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = (self.request.query_params.get('search') or self.request.query_params.get('q') or '').strip()
        if not q:
            return queryset
        from django.db.models import Q
        from django.db.models.functions import Cast
        from django.db.models import CharField
        q_lower = q.lower()
        base_q = (
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(barcode__icontains=q) |
            Q(gtin__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )
        if q_lower == 'ativo':
            return queryset.filter(is_active=True)
        if q_lower == 'inativo':
            return queryset.filter(is_active=False)
        try:
            from decimal import Decimal
            _ = Decimal(q.replace(',', '.'))
            queryset = queryset.annotate(
                cost_str=Cast('cost_price', CharField()),
                price_str=Cast('sale_price', CharField()),
                stock_str=Cast('stock_quantity', CharField()),
            )
            base_q = base_q | Q(cost_str__icontains=q.replace(',', '.')) | Q(price_str__icontains=q.replace(',', '.')) | Q(stock_str__icontains=q)
        except Exception:
            pass
        return queryset.filter(base_q)

    @action(detail=True, methods=['patch'], url_path='pricing')
    def pricing(self, request, pk=None):
        """PATCH pricing: profit_margin or sale_price + price_manually_set."""
        product = self.get_object()
        serializer = ProductPricingSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProductSerializer(product).data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a product."""
        product = self.get_object()
        movements = product.stock_movements.all()[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock."""
        products = Product.objects.filter(
            stock_quantity__lte=models.F('min_stock'),
            is_active=True
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """PDV: search by name (icontains), SKU or GTIN. Returns id, name, sku, gtin, sale_price, stock_balance."""
        q = (request.query_params.get('q') or '').strip()
        if not q:
            return Response([])
        from django.db.models import Q
        products = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(gtin__icontains=q) | Q(barcode__icontains=q)
        )[:20]
        serializer = ProductPdvSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-code')
    def by_code(self, request):
        """PDV: get product by code (SKU or GTIN). Returns 404 if not found."""
        code = (request.query_params.get('code') or '').strip()
        if not code:
            return Response({'detail': 'Parâmetro code é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        from django.db.models import Q
        product = Product.objects.filter(is_active=True).filter(
            Q(sku=code) | Q(gtin=code) | Q(barcode=code)
        ).first()
        if not product:
            return Response({'detail': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductPdvSerializer(product)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Excluir produto; retorna mensagem clara se houver vendas/compras vinculadas."""
        product = self.get_object()
        try:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as e:
            return Response(
                {
                    'error': (
                        'Não é possível excluir este produto pois existem vendas, '
                        'compras ou itens de NF-e vinculados. Desative o produto (marcar como inativo) em vez de excluir.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StockMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for Stock Movement management."""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filterset_fields = ['product', 'movement_type']

    def get_queryset(self):
        queryset = StockMovement.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by('-created_at')


class PurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Purchase (read-only list/detail)."""
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filterset_fields = []
    search_fields = ['supplier_name', 'nfe_key', 'nfe_number']
