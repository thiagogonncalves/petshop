from django.contrib import admin
from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sale_price', 'stock_quantity', 'is_low_stock', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'barcode', 'sku')
    readonly_fields = ('created_at', 'updated_at', 'profit_margin')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'new_stock', 'created_at', 'created_by')
    list_filter = ('movement_type', 'created_at')
    readonly_fields = ('previous_stock', 'new_stock', 'created_at', 'created_by')
