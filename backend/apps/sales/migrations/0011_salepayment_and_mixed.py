# Migration: SalePayment for split payments + mixed choice

from decimal import Decimal
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_add_cancellation_reason'),
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
                    ('mixed', 'Misto (várias formas)'),
                ],
                max_length=20,
                verbose_name='Forma de Pagamento',
            ),
        ),
        migrations.CreateModel(
            name='SalePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(
                    choices=[
                        ('cash', 'Dinheiro'),
                        ('credit_card', 'Cartão de Crédito'),
                        ('debit_card', 'Cartão de Débito'),
                        ('pix', 'PIX'),
                        ('bank_transfer', 'Transferência Bancária'),
                        ('installment', 'Parcelado'),
                    ],
                    max_length=20,
                    verbose_name='Forma de Pagamento',
                )),
                ('amount', models.DecimalField(
                    decimal_places=2,
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(Decimal('0.01'))],
                    verbose_name='Valor',
                )),
                ('sale', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payments',
                    to='sales.sale',
                    verbose_name='Venda',
                )),
            ],
            options={
                'verbose_name': 'Pagamento da Venda',
                'verbose_name_plural': 'Pagamentos da Venda',
            },
        ),
    ]
