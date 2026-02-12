"""
Modelos fiscais - configuração SEFAZ e importação NF-e.
"""
from django.db import models


class CompanyFiscalConfig(models.Model):
    """Configuração fiscal da empresa (certificado A1, CNPJ, UF)."""
    company = models.OneToOneField(
        'users.CompanySettings',
        on_delete=models.CASCADE,
        related_name='fiscal_config',
        verbose_name='Empresa'
    )
    cnpj = models.CharField(max_length=14, verbose_name='CNPJ')
    uf = models.CharField(max_length=2, verbose_name='UF')
    cert_pfx_encrypted = models.BinaryField(
        blank=True,
        null=True,
        verbose_name='Certificado PFX (criptografado)'
    )
    cert_password_encrypted = models.TextField(
        blank=True,
        null=True,
        verbose_name='Senha do certificado (criptografada)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    last_nsu = models.CharField(max_length=20, default='0', verbose_name='Último NSU')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração fiscal'
        verbose_name_plural = 'Configurações fiscais'

    def __str__(self):
        return f'Config fiscal - {self.company.name or self.cnpj}'


class NFeImportStatus(models.TextChoices):
    PENDING = 'pending', 'Pendente'
    PROCESSING = 'processing', 'Processando'
    IMPORTED = 'imported', 'Importado'
    ERROR = 'error', 'Erro'


class NFeImport(models.Model):
    """NF-e importada via SEFAZ (Distribuição DF-e)."""
    company = models.ForeignKey(
        'users.CompanySettings',
        on_delete=models.CASCADE,
        related_name='fiscal_nfe_imports',
        verbose_name='Empresa'
    )
    access_key = models.CharField(max_length=44, verbose_name='Chave de acesso', db_index=True)
    nsu = models.CharField(max_length=20, blank=True, null=True, verbose_name='NSU')
    schema = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Schema'
    )  # ex: resNFe, procNFe
    status = models.CharField(
        max_length=20,
        choices=NFeImportStatus.choices,
        default=NFeImportStatus.PENDING,
        verbose_name='Status'
    )
    sefaz_cstat = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Código retorno SEFAZ'
    )
    sefaz_xmotivo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo retorno SEFAZ'
    )
    resumo_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Resumo (metadados)'
    )
    xml_encrypted = models.BinaryField(
        blank=True,
        null=True,
        verbose_name='XML completo (criptografado)'
    )
    xml_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Hash SHA256 do XML'
    )
    imported_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fiscal_nfe_imports',
        verbose_name='Importado por'
    )
    imported_at = models.DateTimeField(blank=True, null=True, verbose_name='Importado em')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Importação NF-e (fiscal)'
        verbose_name_plural = 'Importações NF-e (fiscal)'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'access_key'],
                name='fiscal_nfeimport_company_access_key_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['company', 'access_key']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'imported_at']),
        ]

    def __str__(self):
        return f'NF-e {self.access_key[:20]}... - {self.status}'

    @property
    def has_xml(self):
        return bool(self.xml_encrypted)


class NFeItem(models.Model):
    """Item da NF-e (quando XML completo disponível)."""
    nfe_import = models.ForeignKey(
        NFeImport,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Importação NF-e'
    )
    item_number = models.PositiveIntegerField(verbose_name='Número do item')
    description = models.CharField(max_length=500, verbose_name='Descrição')
    ncm = models.CharField(max_length=10, blank=True, verbose_name='NCM')
    cfop = models.CharField(max_length=4, blank=True, verbose_name='CFOP')
    qty = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        verbose_name='Quantidade'
    )
    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        verbose_name='Preço unitário'
    )
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Total'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item NF-e'
        verbose_name_plural = 'Itens NF-e'
        ordering = ['item_number']
        unique_together = [['nfe_import', 'item_number']]

    def __str__(self):
        return f'{self.item_number} - {self.description[:50]}'
