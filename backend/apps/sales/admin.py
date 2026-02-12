from django.contrib import admin
from .models import Sale, SaleItem, SalePayment, Receipt, Invoice, CreditAccount, CreditInstallment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total',)


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0
    readonly_fields = ('payment_method', 'amount')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total', 'payment_method', 'status', 'sale_date', 'created_by')
    list_filter = ('status', 'payment_method', 'sale_date')
    search_fields = ('client__name', 'id')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'subtotal', 'total')
    inlines = [SaleItemInline, SalePaymentInline]


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


class CreditInstallmentInline(admin.TabularInline):
    model = CreditInstallment
    extra = 0
    readonly_fields = ('number', 'due_date', 'amount', 'status', 'paid_at', 'paid_amount', 'paid_by')


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'client', 'financed_amount', 'installments_count', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__name', 'client__document')
    readonly_fields = ('created_at', 'created_by')
    inlines = [CreditInstallmentInline]


@admin.register(CreditInstallment)
class CreditInstallmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'credit_account', 'number', 'due_date', 'amount', 'status', 'paid_at', 'paid_by')
    list_filter = ('status', 'credit_account')
