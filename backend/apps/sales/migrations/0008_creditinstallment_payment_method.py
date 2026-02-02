# Generated - add payment_method to CreditInstallment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_credit_account_and_installments'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditinstallment',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cash', 'Dinheiro'),
                    ('credit_card', 'Cartão de Crédito'),
                    ('debit_card', 'Cartão de Débito'),
                    ('pix', 'PIX'),
                    ('bank_transfer', 'Transferência Bancária'),
                ],
                default='',
                max_length=20,
                verbose_name='Forma de pagamento'
            ),
            preserve_default=False,
        ),
    ]
