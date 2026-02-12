"""
Serializers do módulo fiscal.
"""
from rest_framework import serializers
from .models import CompanyFiscalConfig, NFeImport, NFeItem


class CompanyFiscalConfigSerializer(serializers.ModelSerializer):
    """Configuração fiscal (nunca expõe cert/senha)."""

    class Meta:
        model = CompanyFiscalConfig
        fields = [
            'id', 'cnpj', 'uf', 'is_active', 'last_nsu',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'last_nsu', 'created_at', 'updated_at']


class CompanyFiscalConfigCreateUpdateSerializer(serializers.Serializer):
    """Upload de PFX e senha para criar/atualizar config."""
    cnpj = serializers.CharField(max_length=14)
    uf = serializers.CharField(max_length=2)
    pfx_file = serializers.FileField(write_only=True)
    pfx_password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class NFeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFeItem
        fields = [
            'id', 'item_number', 'description', 'ncm', 'cfop',
            'qty', 'unit_price', 'total',
        ]


class NFeImportListSerializer(serializers.ModelSerializer):
    """Lista de NF-e com campos resumidos."""
    emitente = serializers.SerializerMethodField()
    data_emissao = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()
    tem_xml = serializers.SerializerMethodField()

    class Meta:
        model = NFeImport
        fields = [
            'id', 'access_key', 'emitente', 'data_emissao', 'valor_total',
            'status', 'tem_xml', 'nsu', 'created_at',
        ]

    def get_emitente(self, obj):
        if obj.resumo_json:
            return obj.resumo_json.get('emitente') or obj.resumo_json.get('emitente_cnpj') or '-'
        return '-'

    def get_data_emissao(self, obj):
        if obj.resumo_json:
            return obj.resumo_json.get('data_emissao') or '-'
        return '-'

    def get_valor_total(self, obj):
        if obj.resumo_json:
            return obj.resumo_json.get('valor_total') or '-'
        return '-'

    def get_tem_xml(self, obj):
        return bool(obj.xml_encrypted)


class NFeImportDetailSerializer(serializers.ModelSerializer):
    """Detalhe completo da NF-e (resumo_json formatado, itens)."""
    items = NFeItemSerializer(many=True, read_only=True)
    resumo = serializers.SerializerMethodField()
    tem_xml = serializers.SerializerMethodField()

    class Meta:
        model = NFeImport
        fields = [
            'id', 'access_key', 'nsu', 'schema', 'status',
            'sefaz_cstat', 'sefaz_xmotivo',
            'resumo', 'items', 'tem_xml',
            'imported_by', 'imported_at', 'created_at', 'updated_at',
        ]

    def get_resumo(self, obj):
        return obj.resumo_json or {}

    def get_tem_xml(self, obj):
        return bool(obj.xml_encrypted)
