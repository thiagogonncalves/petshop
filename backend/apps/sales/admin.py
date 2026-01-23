from django.contrib import admin
from .models import Sale, SaleItem, Receipt, Invoice


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total', 'payment_method', 'status', 'sale_date', 'created_by')
    list_filter = ('status', 'payment_method', 'sale_date')
    search_fields = ('client__name', 'id')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'subtotal', 'total')
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'item_type', 'quantity', 'unit_price', 'total')
    list_filter = ('item_type',)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'sale', 'issued_at')
    readonly_fields = ('issued_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'sale', 'issued_at')
    readonly_fields = ('issued_at',)
