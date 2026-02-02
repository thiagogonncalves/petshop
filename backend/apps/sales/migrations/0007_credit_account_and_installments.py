# Generated for Crediário da Casa (Store Credit) module

from decimal import Decimal
import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0006_reports_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cash', 'Dinheiro'),
                    ('credit_card', 'Cartão de Crédito'),
                    ('debit_card', 'Cartão de Débito'),
                    ('pix', 'PIX'),
                    ('bank_transfer', 'Transferência Bancária'),
                    ('installment', 'Parcelado'),
                    ('crediario', 'Crediário da Casa'),
                ],
                max_length=20,
                verbose_name='Forma de Pagamento'
            ),
        ),
        migrations.AlterField(
            model_name='sale',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendente'),
                    ('paid', 'Pago'),
                    ('credit_open', 'Crediário em aberto'),
                    ('cancelled', 'Cancelado'),
                    ('refunded', 'Reembolsado'),
                ],
                default='pending',
                max_length=15,
                verbose_name='Status'
            ),
        ),
        migrations.CreateModel(
            name='CreditAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Valor total')),
                ('down_payment', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Entrada')),
                ('financed_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Valor financiado')),
                ('installments_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2)], verbose_name='Número de parcelas')),
                ('status', models.CharField(choices=[('open', 'Em aberto'), ('settled', 'Quitado'), ('cancelled', 'Cancelado')], default='open', max_length=15, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='credit_accounts', to='clients.client', verbose_name='Cliente')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_credit_accounts', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('sale', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='credit_account', to='sales.sale', verbose_name='Venda')),
            ],
            options={
                'verbose_name': 'Crediário',
                'verbose_name_plural': 'Crediários',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CreditInstallment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='Número da parcela')),
                ('due_date', models.DateField(verbose_name='Data de vencimento')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Valor')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('paid', 'Pago'), ('overdue', 'Atrasado'), ('cancelled', 'Cancelado')], default='pending', max_length=15, verbose_name='Status')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='Data do pagamento')),
                ('paid_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor pago')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('credit_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='installments', to='sales.creditaccount', verbose_name='Crediário')),
                ('paid_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paid_installments', to=settings.AUTH_USER_MODEL, verbose_name='Pago por')),
            ],
            options={
                'verbose_name': 'Parcela',
                'verbose_name_plural': 'Parcelas',
                'ordering': ['credit_account', 'number'],
                'unique_together': {('credit_account', 'number')},
            },
        ),
        migrations.AddIndex(
            model_name='creditaccount',
            index=models.Index(fields=['client', 'status'], name='sales_credit_client__idx'),
        ),
        migrations.AddIndex(
            model_name='creditaccount',
            index=models.Index(fields=['status'], name='sales_credit_status_idx'),
        ),
        migrations.AddIndex(
            model_name='creditinstallment',
            index=models.Index(fields=['due_date', 'status'], name='sales_credit_due_dat_idx'),
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['created_at', 'payment_method'], name='sales_sale_created_pay_idx'),
        ),
    ]
