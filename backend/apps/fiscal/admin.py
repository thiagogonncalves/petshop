from django.contrib import admin
from .models import CompanyFiscalConfig, NFeImport, NFeItem


@admin.register(CompanyFiscalConfig)
class CompanyFiscalConfigAdmin(admin.ModelAdmin):
    list_display = ['company', 'cnpj', 'uf', 'is_active', 'last_nsu', 'updated_at']
    list_filter = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


class NFeItemInline(admin.TabularInline):
    model = NFeItem
    extra = 0
    readonly_fields = ['item_number', 'description', 'ncm', 'cfop', 'qty', 'unit_price', 'total']


@admin.register(NFeImport)
class NFeImportAdmin(admin.ModelAdmin):
    list_display = ['access_key', 'company', 'status', 'sefaz_cstat', 'has_xml', 'imported_at', 'created_at']
    list_filter = ['status', 'company']
    search_fields = ['access_key']
    readonly_fields = ['access_key', 'nsu', 'schema', 'sefaz_cstat', 'sefaz_xmotivo', 'resumo_json', 'xml_hash', 'imported_at', 'created_at', 'updated_at']
    inlines = [NFeItemInline]

    def has_xml(self, obj):
        return bool(obj.xml_encrypted)
    has_xml.boolean = True
    has_xml.short_description = 'Tem XML'
