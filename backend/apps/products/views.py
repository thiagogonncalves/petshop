"""
Product views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Category, Product, StockMovement
from .serializers import CategorySerializer, ProductSerializer, StockMovementSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category management
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product management
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'barcode', 'sku']

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a product"""
        product = self.get_object()
        movements = product.stock_movements.all()[:50]  # Last 50 movements
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = Product.objects.filter(
            stock_quantity__lte=models.F('min_stock'),
            is_active=True
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Stock Movement management
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filterset_fields = ['product', 'movement_type']
    
    def get_queryset(self):
        queryset = StockMovement.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by('-created_at')
