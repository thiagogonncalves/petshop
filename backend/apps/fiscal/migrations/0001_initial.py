# Generated manually for fiscal module

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_user_must_change_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyFiscalConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(max_length=14, verbose_name='CNPJ')),
                ('uf', models.CharField(max_length=2, verbose_name='UF')),
                ('cert_pfx_encrypted', models.BinaryField(blank=True, null=True, verbose_name='Certificado PFX (criptografado)')),
                ('cert_password_encrypted', models.TextField(blank=True, null=True, verbose_name='Senha do certificado (criptografada)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('last_nsu', models.CharField(default='0', max_length=20, verbose_name='Último NSU')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fiscal_config', to='users.companysettings', verbose_name='Empresa')),
            ],
            options={
                'verbose_name': 'Configuração fiscal',
                'verbose_name_plural': 'Configurações fiscais',
            },
        ),
        migrations.CreateModel(
            name='NFeImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_key', models.CharField(db_index=True, max_length=44, verbose_name='Chave de acesso')),
                ('nsu', models.CharField(blank=True, max_length=20, null=True, verbose_name='NSU')),
                ('schema', models.CharField(blank=True, max_length=20, null=True, verbose_name='Schema')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('processing', 'Processando'), ('imported', 'Importado'), ('error', 'Erro')], default='pending', max_length=20, verbose_name='Status')),
                ('sefaz_cstat', models.CharField(blank=True, max_length=10, null=True, verbose_name='Código retorno SEFAZ')),
                ('sefaz_xmotivo', models.TextField(blank=True, null=True, verbose_name='Motivo retorno SEFAZ')),
                ('resumo_json', models.JSONField(blank=True, null=True, verbose_name='Resumo (metadados)')),
                ('xml_encrypted', models.BinaryField(blank=True, null=True, verbose_name='XML completo (criptografado)')),
                ('xml_hash', models.CharField(blank=True, max_length=64, null=True, verbose_name='Hash SHA256 do XML')),
                ('imported_at', models.DateTimeField(blank=True, null=True, verbose_name='Importado em')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fiscal_nfe_imports', to='users.companysettings', verbose_name='Empresa')),
                ('imported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fiscal_nfe_imports', to=settings.AUTH_USER_MODEL, verbose_name='Importado por')),
            ],
            options={
                'verbose_name': 'Importação NF-e (fiscal)',
                'verbose_name_plural': 'Importações NF-e (fiscal)',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NFeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_number', models.PositiveIntegerField(verbose_name='Número do item')),
                ('description', models.CharField(max_length=500, verbose_name='Descrição')),
                ('ncm', models.CharField(blank=True, max_length=10, verbose_name='NCM')),
                ('cfop', models.CharField(blank=True, max_length=4, verbose_name='CFOP')),
                ('qty', models.DecimalField(decimal_places=4, default=0, max_digits=14, verbose_name='Quantidade')),
                ('unit_price', models.DecimalField(decimal_places=4, default=0, max_digits=14, verbose_name='Preço unitário')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('nfe_import', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='fiscal.nfeimport', verbose_name='Importação NF-e')),
            ],
            options={
                'verbose_name': 'Item NF-e',
                'verbose_name_plural': 'Itens NF-e',
                'ordering': ['item_number'],
                'unique_together': {('nfe_import', 'item_number')},
            },
        ),
        migrations.AddConstraint(
            model_name='nfeimport',
            constraint=models.UniqueConstraint(fields=('company', 'access_key'), name='fiscal_nfeimport_company_access_key_unique'),
        ),
        migrations.AddIndex(
            model_name='nfeimport',
            index=models.Index(fields=['company', 'access_key'], name='fiscal_nfei_company_7a458a_idx'),
        ),
        migrations.AddIndex(
            model_name='nfeimport',
            index=models.Index(fields=['company', 'status'], name='fiscal_nfei_company_d79c60_idx'),
        ),
        migrations.AddIndex(
            model_name='nfeimport',
            index=models.Index(fields=['company', 'imported_at'], name='fiscal_nfei_company_3e5a5c_idx'),
        ),
    ]
