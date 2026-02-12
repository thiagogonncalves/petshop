# Migration: add change_amount (troco) to Sale

from decimal import Decimal
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_salepayment_and_mixed'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='change_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Valor do troco devolvido ao cliente (pagamento em dinheiro)',
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
                verbose_name='Troco',
            ),
        ),
    ]
